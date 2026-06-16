"""② 選別：候補をまとめて Claude に渡し、研究プロファイルに最も合う上位本を選ばせる。"""
import json
import anthropic
from . import config

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY を環境変数から読む


def select_top(papers, k=None):
    k = k or config.EPISODES_PER_RUN
    if not papers:
        return []
    if len(papers) <= k:
        return papers

    listing = "\n\n".join(
        f"[{i}] {p['title']}\n掲載: {p.get('venue')}\n要旨: {p['abstract'][:600]}"
        for i, p in enumerate(papers)
    )
    prompt = (
        f"次の研究者プロファイルに最も関連が深く、聴く価値の高い論文を上位{k}本だけ選んでください。\n"
        f"重複テーマは避け、手法や知見の新しさを重視してください。\n\n"
        f"# 研究者プロファイル\n{config.RESEARCH_PROFILE}\n\n"
        f"# 候補論文\n{listing}\n\n"
        f"出力は選んだ番号のJSON配列のみ。例: [3, 0, 7]"
    )
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip().replace("```json", "").replace("```", "")
    try:
        idxs = json.loads(text)
        chosen = [papers[i] for i in idxs if 0 <= i < len(papers)][:k]
    except Exception as e:
        print(f"  [warn] 選別パース失敗、先頭{k}本を採用: {e}")
        chosen = papers[:k]
    print(f"  選別: {len(chosen)} 本を採用")
    return chosen
