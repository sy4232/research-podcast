"""③④ 要約＋台本：論文ごとに日本語の2人対話台本を生成する。"""
import anthropic
from . import config

client = anthropic.Anthropic()

SYSTEM = (
    "あなたは都市気候の専門知識を持つ科学ポッドキャストの構成作家です。"
    "聴き手は同分野の博士課程研究者。専門用語は残しつつ、なぜ重要か・既存研究との差分・"
    "手法の妥当性・限界を、自然な日本語の会話で伝えます。"
)


def make_dialogue(paper, intro=False):
    """論文1本ぶんの対話台本（『あかり: …』『けんた: …』の行のみ）を返す。"""
    a, b = config.HOST_A_NAME, config.HOST_B_NAME
    intro_line = (
        f"最初の数行で番組名「{config.PODCAST_TITLE}」と今回の概要に軽く触れてから本題へ。\n"
        if intro else ""
    )
    if paper.get("kind") == "highly_cited":
        context_line = (
            f"※この論文は新着ではなく、直近数年で被引用数{paper.get('cited_by_count', 0)}回の"
            f"よく引用されている重要論文です。なぜ広く引用され影響を持つのかにも触れてください。\n"
        )
    else:
        context_line = "※この論文は直近の新着論文です。新規性がどこにあるかを明確に。\n"
    prompt = (
        f"次の論文を、2人のホスト（{a}=聞き手、{b}=解説役）の日本語対話にしてください。\n"
        f"4〜6分相当（おおよそ900〜1300字）。冗長な相槌は避け、中身を濃く。\n"
        f"{context_line}{intro_line}"
        f"出力は各行『{a}: …』または『{b}: …』の形式のみ。見出しや注釈は不要。\n\n"
        f"# 論文\nタイトル: {paper['title']}\n掲載: {paper.get('venue')}\n"
        f"DOI: {paper.get('doi')}\n要旨: {paper['abstract']}"
    )
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=2500,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
