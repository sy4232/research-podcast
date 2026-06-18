"""③④ 論文台本：学会の質疑応答形式（発表者プレゼン＋批判的な討論者のQ&A）を日本語で生成。"""
import anthropic
from . import config

client = anthropic.Anthropic()

SYSTEM = (
    "あなたは都市気候系の国際学会で、鋭い洞察で知られる座長兼ディスカッサントの構成を担う作家です。"
    "登壇者の発表のあと、討論者が研究の核心・前提・限界を批判的に突く、密度の高い質疑を日本語で構成します。"
)


def make_qa(paper, intro=False):
    """論文1本ぶんの『発表＋批判的質疑』台本（話者行のみ）を返す。約8分＝2000〜2400字。"""
    pres, _ = config.PAPER_PRESENTER
    disc, _ = config.PAPER_DISCUSSANT
    cites = paper.get("cited_by_count", 0)
    if paper.get("kind") == "highly_cited":
        framing = (
            f"これは新着ではなく直近{config.FALLBACK_YEARS}年で被引用数{cites}回の重要論文。"
            "なぜ広く引用され影響力を持つのか、その上で見落とされがちな弱点は何かを討論者が突くこと。"
        )
    else:
        framing = "これは最新の新着論文。新規性の核がどこにあるかを明確にしたうえで、その新規性の妥当性を討論者が検証すること。"
    intro_line = (
        f"冒頭で番組名「{config.PODCAST_TITLE}」と本日の論文タイトルに一言触れてから発表に入る。\n"
        if intro else ""
    )
    prompt = (
        f"次の論文について、学会の質疑応答形式の日本語台本を作ってください。\n"
        f"登場人物は2名：『{pres}』（論文の著者になりきって発表・応答）と『{disc}』（批判的洞察に長けた討論者）。\n"
        f"構成：{intro_line}"
        f"(1){pres}が研究の動機・手法・主要な結果を3〜4分相当で発表 →"
        f"(2){disc}が前提・手法の妥当性・データやベースラインの限界・一般化可能性・反証可能性などを"
        f"鋭く問い、{pres}が誠実に応答する質疑を3〜4分相当。\n"
        f"討論者は遠慮せず核心を突くが、フェアで建設的に。専門用語は残し、中身を濃く。全体で約2000〜2400字。\n"
        f"{framing}\n"
        f"出力は各行『{pres}: …』または『{disc}: …』の形式のみ。見出し・ト書き・注釈は書かない。\n\n"
        f"# 論文\nタイトル: {paper['title']}\n掲載: {paper.get('venue')}\n"
        f"DOI: {paper.get('doi')}\n要旨: {paper['abstract']}"
    )
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=4000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
