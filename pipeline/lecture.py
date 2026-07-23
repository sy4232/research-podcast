"""上級・都市微気候 講義シリーズ（全5回）の台本生成。講師＋受講生の2話者。"""
import anthropic
from . import config

client = anthropic.Anthropic()

SYSTEM = (
    "あなたは都市気候学の大学院上級講義を担当する教員です。"
    "受講者は都市気候を専門とする博士課程の研究者であり、教科書的な入門説明は不要です。"
    "概念の背後にある仮定・近似・限界、そして研究実務での落とし穴を、物理の言葉で正確に説明します。"
    "重要：具体的な数値・年号・論文の著者名や出典を断定的に述べないこと。"
    "確立した枠組みや手法の一般名（例：Monin-Obukhov相似則、Penman-Monteith、LCZ）に言及するのは可だが、"
    "不確かな引用や統計値を創作してはならない。曖昧な点は『一般に〜とされる』と留保をつけて述べる。"
)


def make_lecture(spec):
    """講義1回ぶんの台本（話者行のみ）を返す。約13分＝3200〜3800字。"""
    lec, _ = config.LECTURER_VOICE
    stu, _ = config.STUDENT_VOICE
    topics = "\n".join(f"  - {t}" for t in spec["topics"])
    total = len(config.LECTURES)
    prompt = (
        f"都市微気候の上級講義シリーズ（全{total}回）の第{spec['no']}回の日本語台本を作ってください。\n"
        f"題目：{spec['title']}\n"
        f"この回の狙い：{spec['hook']}\n\n"
        f"扱う内容：\n{topics}\n\n"
        f"登場人物は2名：『{lec}』（体系立てて講義する）と『{stu}』"
        f"（博士課程の受講者。理解の要所で『なぜそう言えるのか』『実務では何が問題になるか』と鋭く質問する）。\n"
        f"構成：冒頭で番組名「{config.PODCAST_TITLE}」と、全{total}回中の第{spec['no']}回であること、"
        f"今回の位置づけを簡潔に述べてから講義へ。最後に要点の総括と、次回への橋渡しを一言"
        f"（第{total}回の場合はシリーズ完結の言葉）。\n"
        f"長さは約{config.LECTURE_MINUTES}分相当（3200〜3800字）。密度を優先し、冗長な相槌は書かない。\n"
        f"出力は各行『{lec}: …』または『{stu}: …』の形式のみ。見出し・ト書き・注釈は書かない。"
    )
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def next_lecture(published_numbers):
    """未配信の最小の回を返す。全5回が済んでいればNone。"""
    for spec in config.LECTURES:
        if spec["no"] not in published_numbers:
            return spec
    return None
