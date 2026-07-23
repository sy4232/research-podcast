"""BUCSS登壇者の論文収集：OpenAlexで著者を同定し、その人の代表的な論文を取得する。
配信順は config.BUCSS_LECTURERS の並び（＝キャリア接続の強い順）。"""
import re
import requests
from . import config

AUTHORS = "https://api.openalex.org/authors"
WORKS = "https://api.openalex.org/works"


def _norm(s):
    return re.sub(r"[^a-z]", "", (s or "").lower())


def resolve_author(name, inst):
    """著者名＋所属からOpenAlexの著者IDを同定する。所属一致を優先し、無ければ最有力候補。"""
    try:
        r = requests.get(AUTHORS, params={"search": name, "per-page": 10,
                                          "mailto": config.OPENALEX_MAILTO}, timeout=40)
        r.raise_for_status()
        results = r.json().get("results", [])
    except requests.RequestException as e:
        print(f"  [warn] 著者検索失敗 ({name}): {e}")
        return None
    if not results:
        return None

    want_inst = _norm(inst)
    want_name = _norm(name)
    best = None
    for a in results:
        # 所属候補を集める（APIの版differencesに備え複数フィールドを見る）
        insts = []
        for it in (a.get("last_known_institutions") or []):
            insts.append(it.get("display_name", ""))
        legacy = a.get("last_known_institution")          # 旧API（単数形）
        if isinstance(legacy, dict):
            insts.append(legacy.get("display_name", ""))
        for af in (a.get("affiliations") or []):
            insts.append((af.get("institution") or {}).get("display_name", ""))
        inst_hit = any(want_inst and want_inst[:12] in _norm(i) for i in insts)
        name_hit = want_name in _norm(a.get("display_name", ""))
        if inst_hit and name_hit:
            return a          # 所属も名前も一致＝確度が高い
        if best is None and name_hit:
            best = a
    return best or results[0]


def fetch_lecturer_papers(lect, exclude_ids, need=None):
    """登壇者1名の論文候補を返す（新しい順＋被引用の多い順を混ぜて多めに）。"""
    need = need or config.BUCSS_PAPERS_PER_EP
    a = resolve_author(lect["name"], lect["inst"])
    if not a:
        print(f"  [warn] 著者が見つかりません: {lect['name']}")
        return []
    aid = str(a["id"]).rstrip("/").split("/")[-1]   # URL形式でも短縮IDでも動くように
    print(f"  著者同定: {a.get('display_name')} ({aid}) 総論文数={a.get('works_count')}")

    found = {}
    for sort in ("publication_date:desc", "cited_by_count:desc"):
        try:
            r = requests.get(WORKS, params={
                "filter": f"author.id:{aid},type:article",
                "sort": sort, "per-page": 25, "mailto": config.OPENALEX_MAILTO,
            }, timeout=40)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"  [warn] 論文取得失敗 ({lect['name']}/{sort}): {e}")
            continue
        for w in r.json().get("results", []):
            wid = w["id"]
            if wid in exclude_ids or wid in found:
                continue
            from .fetch import _reconstruct_abstract
            abstract = _reconstruct_abstract(w.get("abstract_inverted_index"))
            if len(abstract) < 120:
                continue
            src = (w.get("primary_location") or {}).get("source") or {}
            found[wid] = {
                "id": wid,
                "title": w.get("display_name") or "(no title)",
                "abstract": abstract,
                "doi": w.get("doi"),
                "venue": src.get("display_name"),
                "date": w.get("publication_date"),
                "cited_by_count": w.get("cited_by_count", 0),
                "lecturer": lect["name"],
            }
    papers = list(found.values())
    print(f"  {lect['name']}: 候補 {len(papers)} 本")
    return papers


def next_lecturer(published_names):
    """まだ取り上げていない登壇者を、配信順（キャリア接続順）で1名返す。全員済みならNone。"""
    for lect in config.BUCSS_LECTURERS:
        if lect["name"] not in published_names:
            return lect
    return None
