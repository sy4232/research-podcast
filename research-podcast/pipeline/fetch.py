"""① 論文収集：OpenAlex から直近の論文を取得（ジャーナル＋プレプリントを広くカバー、APIキー不要）。"""
import datetime
import requests
from . import config

OPENALEX = "https://api.openalex.org/works"


def _reconstruct_abstract(inv):
    """OpenAlex は abstract を inverted index で返すので語順を復元する。"""
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch_recent(seen_ids):
    """seen_ids にない直近論文を dict のリストで返す。"""
    since = (datetime.date.today() - datetime.timedelta(days=config.SINCE_DAYS)).isoformat()
    found = {}
    for term in config.TOPICS:
        params = {
            "search": term,
            "filter": f"from_publication_date:{since},type:article",
            "sort": "relevance_score:desc",
            "per-page": config.PER_TOPIC,
            "mailto": config.OPENALEX_MAILTO,
        }
        try:
            r = requests.get(OPENALEX, params=params, timeout=40)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"  [warn] OpenAlex 取得失敗 ({term}): {e}")
            continue
        for w in r.json().get("results", []):
            wid = w["id"]
            if wid in seen_ids or wid in found:
                continue
            abstract = _reconstruct_abstract(w.get("abstract_inverted_index"))
            if len(abstract) < 120:          # アブストが無い/短すぎるものは除外
                continue
            src = (w.get("primary_location") or {}).get("source") or {}
            found[wid] = {
                "id": wid,
                "title": w.get("display_name") or "(no title)",
                "abstract": abstract,
                "doi": w.get("doi"),
                "venue": src.get("display_name"),
                "date": w.get("publication_date"),
            }
    papers = list(found.values())
    print(f"  収集: 新規候補 {len(papers)} 本")
    return papers
