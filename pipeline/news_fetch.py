"""政策ウォッチ①収集：GDELT DOC 2.0 ＋ RSS ＋ Federal Register。
本文は取得せず、見出し/配信元要約（RSSのdescription, FRのabstract）のみを使う＝著作権安全。"""
import time
import datetime
import requests
from . import config

try:
    import feedparser
except Exception:
    feedparser = None

UA = {"User-Agent": "UrbanClimateDigest/1.0 (personal research)"}


def _gdelt():
    """GDELT DOC 2.0 artlist。キー不要・REST。見出し＋URL＋メタのみ返る。"""
    if not config.NEWS_USE_GDELT:
        return []
    query = "(" + " OR ".join(f'"{k}"' for k in config.NEWS_KEYWORDS) + ")"
    params = {
        "query": query, "mode": "artlist", "format": "json",
        "timespan": f"{config.NEWS_TIMESPAN_HOURS}h", "maxrecords": 75, "sort": "datedesc",
    }
    out = []
    try:
        r = requests.get("https://api.gdeltproject.org/api/v2/doc/doc",
                         params=params, headers=UA, timeout=40)
        r.raise_for_status()
        for a in r.json().get("articles", []):
            out.append({
                "title": a.get("title", ""), "summary": "",   # GDELTは本文要約なし→見出しのみ
                "url": a.get("url"), "source": a.get("domain", "GDELT"),
                "date": a.get("seendate", ""),
            })
    except Exception as e:
        print(f"  [warn] GDELT失敗: {e}")
    return out


def _rss():
    if feedparser is None:
        print("  [warn] feedparser未導入のためRSSスキップ")
        return []
    out = []
    for url in config.NEWS_RSS_FEEDS:
        try:
            d = feedparser.parse(url, request_headers=UA)
            for e in d.entries[:20]:
                out.append({
                    "title": e.get("title", ""),
                    "summary": (e.get("summary") or e.get("description") or "")[:600],
                    "url": e.get("link"),
                    "source": d.feed.get("title", url),
                    "date": e.get("published", ""),
                })
        except Exception as ex:
            print(f"  [warn] RSS失敗 ({url}): {ex}")
        time.sleep(0.3)
    return out


def _federal_register():
    """米国官報API。abstract（公開要約）を使用。キー不要。"""
    if not config.NEWS_USE_FEDERAL_REGISTER:
        return []
    since = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    out = []
    try:
        r = requests.get(
            "https://www.federalregister.gov/api/v1/documents.json",
            params={
                "per_page": 30, "order": "newest",
                "conditions[term]": "heat OR climate OR cooling OR building energy",
                "conditions[publication_date][gte]": since,
            },
            headers=UA, timeout=40,
        )
        r.raise_for_status()
        for d in r.json().get("results", []):
            out.append({
                "title": d.get("title", ""),
                "summary": (d.get("abstract") or "")[:600],
                "url": d.get("html_url"),
                "source": "Federal Register / " + ", ".join(d.get("agencies_names", []) or [])[:80],
                "date": d.get("publication_date", ""),
            })
    except Exception as e:
        print(f"  [warn] Federal Register失敗: {e}")
    return out


def fetch_news(seen_urls):
    """全ソースを集約し、既出URLを除外した候補リストを返す。"""
    items = _gdelt() + _rss() + _federal_register()
    uniq = {}
    for it in items:
        u = (it.get("url") or "").strip()
        if not u or u in seen_urls or u in uniq or not it.get("title"):
            continue
        uniq[u] = it
    cands = list(uniq.values())[: config.NEWS_MAX_CANDIDATES]
    print(f"  政策ウォッチ収集: 候補 {len(cands)} 件（GDELT+RSS+FR）")
    return cands
