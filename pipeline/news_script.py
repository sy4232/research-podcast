"""政策ウォッチ②③：候補から話題を選別し、アンカー＋アナリストのブリーフィング台本を生成。
本文は再生産せず、Claudeが自分の言葉で要約し媒体名のみ示す＝著作権安全。"""
import json
import anthropic
from . import config

client = anthropic.Anthropic()

SYSTEM = (
    "あなたは都市気候・都市政策に精通したニュース番組の編集者兼アナリストです。"
    "複数媒体の見出しと配信元要約を読み、重複する報道は1つの話題に束ね、"
    "都市気候研究者にとっての重要度で取捨選択します。"
    "出力では原文を一切引用・転載せず、必ず自分の言葉で要約し、媒体名のみ示します。"
)


def select_stories(cands):
    """候補から都市気候・政策的に重要な話題を NEWS_STORIES 件選び、束ねて返す。"""
    if not cands:
        return []
    listing = "\n\n".join(
        f"[{i}] {c['title']}\n媒体: {c.get('source')}\n要約: {c.get('summary','')[:300]}"
        for i, c in enumerate(cands)
    )
    prompt = (
        f"次の研究者にとって重要な「都市気候・熱・気候政策」の話題を最大{config.NEWS_STORIES}件選んでください。\n"
        f"同じ出来事を複数媒体が報じている場合は1件に束ね、代表となる候補番号をまとめてください。\n\n"
        f"# 研究者プロファイル\n{config.RESEARCH_PROFILE}\n\n# 候補\n{listing}\n\n"
        f"出力はJSONのみ。形式: [{{\"idxs\":[番号,...],\"why\":\"一言でなぜ重要か\"}}, ...]"
    )
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL, max_tokens=800, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip().replace("```json", "").replace("```", "")
    stories = []
    try:
        for s in json.loads(text):
            idxs = [i for i in s.get("idxs", []) if 0 <= i < len(cands)]
            if not idxs:
                continue
            reps = [cands[i] for i in idxs]
            stories.append({
                "title": reps[0]["title"],
                "sources": sorted({r.get("source", "") for r in reps}),
                "summaries": [r.get("summary", "") for r in reps if r.get("summary")],
                "urls": [r.get("url") for r in reps if r.get("url")],
                "why": s.get("why", ""),
            })
    except Exception as e:
        print(f"  [warn] 話題選別パース失敗、先頭{config.NEWS_STORIES}件を採用: {e}")
        for c in cands[: config.NEWS_STORIES]:
            stories.append({"title": c["title"], "sources": [c.get("source", "")],
                            "summaries": [c.get("summary", "")], "urls": [c.get("url")], "why": ""})
    return stories[: config.NEWS_STORIES]


def make_briefing(stories):
    """選ばれた話題群を、アンカー＋アナリストの日本語ブリーフィング台本にする。"""
    anc, _ = config.NEWS_ANCHOR
    ana, _ = config.NEWS_ANALYST
    blocks = "\n\n".join(
        f"■ 話題{i+1}: {s['title']}\n媒体: {', '.join(s['sources'])}\n"
        f"配信元要約: {' / '.join(s['summaries'])[:500]}\n重要な理由: {s['why']}"
        for i, s in enumerate(stories)
    )
    prompt = (
        f"次の話題群を、日本語のニュース・ブリーフィング台本にしてください。約{config.NEWS_MINUTES}分。\n"
        f"登場人物は2名：『{anc}』（要点を簡潔に伝えるアンカー）と『{ana}』"
        f"（都市気候の専門家として、各話題が研究や政策、そして就職活動の文脈でなぜ重要かを一言添える）。\n"
        f"冒頭で番組名「{config.PODCAST_TITLE}」と本日の概況に触れ、各話題をアンカーが紹介→アナリストが解説、の順で。\n"
        f"重要：原文を引用・転載しないこと。必ず自分の言葉で言い換え、媒体名のみ言及する。事実が不確かな点は断定しない。\n"
        f"出力は各行『{anc}: …』または『{ana}: …』の形式のみ。見出し・注釈は不要。\n\n{blocks}"
    )
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL, max_tokens=4000, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
