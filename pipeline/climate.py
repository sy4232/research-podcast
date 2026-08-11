"""シリーズ⑤：地球・都市 気候モデリング講義（全15回）の台本生成。
ナビ（鋭い聞き手）＋ハカセ（専門家）の2話者・テンポの良い掛け合い。
scripts/climate-NN.md があればそれを台本として優先し、無ければ実行時にClaudeで生成する。"""
import os
import anthropic
from . import config

client = anthropic.Anthropic()

SYSTEM = (
    "あなたは地球・都市の気候モデリングの第一線の研究者で、"
    "テンポの良い対談番組のホストを務めています。"
    "聞き手は都市・地球気候を専門とする博士研究者であり、教科書的な入門(101)は不要です。"
    "概念の背後にある仮定・近似・限界、そして研究実務での落とし穴を、物理の言葉で正確に語ります。\n"
    "守るべき作法：\n"
    "(1) 具体的な数値・年号・論文の著者名や出典を断定的に創作しない。"
    "確立した枠組みの一般名（例：Monin-Obukhov相似則、LES、LCZ、Penman-Monteith、CORDEX、SSP）は使ってよい。"
    "不確かな点は『一般に〜とされる』と留保する。\n"
    "(2) 常に『いまどのスケール（地球／メソ／ローカル）を、どの解像度で解いているか』を意識して話す。"
    "スケール間の“つなぎ目”（境界条件・ダウンスケーリング）を要所で明示する。\n"
    "(3) LST（表面温度）は気温(Ta)や人の熱暴露とは別物として扱う。"
    "LSTは表面エネルギー収支・モデルの入力/検証・表面介入の評価・放射/MRT寄与には正当だが、"
    "人口の熱暴露やハザードの代理として使うのは誤り、という区別を守る（cooling pixels ≠ cooling people）。"
)


def make_climate(spec):
    """講義1回ぶんの台本（話者行のみ）を返す。約10分＝2800〜3400字。
    手書き台本 scripts/climate-NN.md があればそれを優先。"""
    path = os.path.join(config.CLIMATE_SCRIPT_DIR, f"climate-{spec['no']:02d}.md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            return text

    navi, _ = config.CLIMATE_NAVI
    hak, _ = config.CLIMATE_HAKASE
    total = len(config.CLIMATE_LECTURES)
    topics = "\n".join(f"  - {t}" for t in spec["topics"])
    nxt = next((s for s in config.CLIMATE_LECTURES if s["no"] == spec["no"] + 1), None)
    bridge = (f"最後に、次回・第{nxt['no']}回「{nxt['title']}」への橋渡しを一言添える。"
              if nxt else f"最後に、全{total}回シリーズの総括で締める。")
    prompt = (
        f"地球・都市の気候モデリング講義シリーズ（全{total}回）の第{spec['no']}回の日本語台本を作ってください。\n"
        f"題目：{spec['title']}\n"
        f"スケール上の位置：{spec['scale']}\n"
        f"今回の狙い：{spec['hook']}\n\n"
        f"扱う内容：\n{topics}\n\n"
        f"話者は2名：『{navi}』（鋭い聞き手。視聴者を代表し、"
        f"『なぜそう言える？』『要するに何が嬉しい？』『どこで破綻する？』とテンポよく切り込み、"
        f"難しい話を日常の言葉で言い換える）と『{hak}』（専門家。物理で正確に答える）。\n"
        f"テンポの良い会話番組のように：短い応酬、適度な言い換え、時に軽い驚きやユーモア。"
        f"ただし中身は玄人向けの密度を保ち、相槌だけの空虚な行は書かない。\n"
        f"構成：冒頭の掴み（ナビの素朴だが本質的な問い）→番組名「{config.PODCAST_TITLE}」と"
        f"全{total}回中の第{spec['no']}回・今回の位置づけを一言→本題（3〜4個の山場）→今回の要点の総括。"
        f"{bridge}\n"
        f"長さは約{config.CLIMATE_MINUTES}分相当（2800〜3400字）。密度を優先する。\n"
        f"出力は各行『{navi}: …』または『{hak}: …』の形式のみ。見出し・ト書き・注釈は書かない。"
    )
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def next_climate(published_numbers):
    """未配信の最小の回を返す。全15回が済んでいればNone。"""
    for spec in config.CLIMATE_LECTURES:
        if spec["no"] not in published_numbers:
            return spec
    return None
