"""中央設定。研究テーマ・話者・モデル・配信URLなどはここだけ変えればOK。"""
import os

# ---- あなたの研究プロファイル（選別の精度を決める。具体的に書くほど良い）----
RESEARCH_PROFILE = (
    "都市システム工学の博士課程の研究者。専門は都市気候・ヒートアイランド緩和・"
    "CFDによる都市微気候シミュレーション・GIS/リモートセンシング・都市緑地の蒸発散冷却・"
    "屋外微気候と建物エネルギーの連成モデリング。応用志向で、公共部門の意思決定支援に関心がある。"
)

# ---- 検索クエリ（OpenAlex の全文検索に投げる語。複数可）----
TOPICS = [
    "urban heat island mitigation",
    "urban microclimate CFD simulation",
    "urban forest evapotranspiration cooling",
    "outdoor thermal comfort GIS remote sensing",
    "coupled indoor outdoor building energy microclimate",
    "urban canopy heat wave land surface temperature",
]

# ---- 収集・選別パラメータ ----
SINCE_DAYS = 7          # 直近何日分を対象にするか（週次なら7）
PER_TOPIC = 20          # 各クエリで取得する最大件数
EPISODES_PER_RUN = 3    # 1エピソードに入れる論文本数（多声TTSは1本ずつ合成して連結）
OPENALEX_MAILTO = os.environ.get("OPENALEX_MAILTO", "you@example.com")  # polite pool用

# ---- LLM（要約・台本生成・選別）----
ANTHROPIC_MODEL = "claude-opus-4-8"   # コスト優先なら "claude-sonnet-4-6"

# ---- 音声（Gemini マルチスピーカーTTS）----
GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
HOST_A_NAME = "あかり"   # 聞き手
HOST_B_NAME = "けんた"   # 解説役
HOST_A_VOICE = "Leda"    # 利用可能ボイスは Gemini TTS のドキュメント参照
HOST_B_VOICE = "Charon"
AUDIO_GAP_SEC = 0.6      # 論文セグメント間の無音

# ---- 配信（GitHub Pages）----
# 例: https://<ユーザー名>.github.io/<リポジトリ名>
PAGES_BASE_URL = os.environ.get("PAGES_BASE_URL", "https://example.github.io/research-podcast").rstrip("/")
PODCAST_TITLE = "都市気候リサーチ・ダイジェスト"
PODCAST_DESC = "自分の研究に関連する最新論文を毎週、日本語の対話形式でお届けする自動生成ポッドキャスト。"
PODCAST_AUTHOR = "Sean"
PODCAST_LANG = "ja"

# ---- パス ----
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
AUDIO_DIR = os.path.join(DOCS_DIR, "audio")
STATE_DIR = os.path.join(REPO_ROOT, "state")
SEEN_PATH = os.path.join(STATE_DIR, "seen.json")
EPISODES_PATH = os.path.join(STATE_DIR, "episodes.json")
