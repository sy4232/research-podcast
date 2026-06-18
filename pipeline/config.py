"""中央設定。両シリーズ（論文Q&A・政策ウォッチ）の設定をここに集約。"""
import os

# =========================================================
#  共通：研究プロファイル / モデル / 配信 / パス
# =========================================================
RESEARCH_PROFILE = (
    "Urban climate researcher focused on mitigating extreme heat and advancing sustainability through rigorous quantification of climate risk."
    "I integrate high-resolution CFD simulations with GIS, remote sensing, and data-driven methods to produce actionable insights that link urban form, infrastructure, and policy to resilient and equitable cities."
)

ANTHROPIC_MODEL = "claude-opus-4-6"   # ※現行Opusは claude-opus-4-8。動かない時はここを変更。コスト優先なら "claude-sonnet-4-6"

# ---- 音声（Gemini マルチスピーカーTTS）----
GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
AUDIO_GAP_SEC = 0.6          # セグメント間の無音
TTS_CHUNK_CHARS = 1100       # 1回のTTS合成に渡す最大文字数（数分超で音質劣化するため分割）
TTS_RETRIES = 6              # TTSの一時失敗（429/稀な500やテキスト返り）に対するリトライ回数
TTS_MIN_INTERVAL_SEC = 20    # ★TTS呼び出しの最小間隔（無料枠のRPMに当たらないよう毎回これだけ空ける）
TTS_BACKOFF_BASE = 30        # 429時のバックオフ基準秒（Retry-Afterヘッダがあればそちら優先）

# ---- 配信（GitHub Pages・単一フィードに両シリーズを混在）----
PAGES_BASE_URL = os.environ.get("PAGES_BASE_URL", "https://sy4232.github.io/research-podcast/").rstrip("/")
PODCAST_TITLE = "Urban Climate Research Digest"
PODCAST_DESC = "都市気候の最新論文（批判的Q&A）と政策・ニュース動向を、日本語でお届けする自動生成ポッドキャスト。"
PODCAST_AUTHOR = "sy4232"
PODCAST_LANG = "ja"

# ---- パス ----
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
AUDIO_DIR = os.path.join(DOCS_DIR, "audio")
PAPER_AUDIO_DIR = os.path.join(AUDIO_DIR, "papers")
NEWS_AUDIO_DIR = os.path.join(AUDIO_DIR, "news")
STATE_DIR = os.path.join(REPO_ROOT, "state")
EPISODES_PATH = os.path.join(STATE_DIR, "episodes.json")   # 両シリーズ共有
SEEN_PATH = os.path.join(STATE_DIR, "seen.json")           # 論文シリーズ（既存）
SEEN_NEWS_PATH = os.path.join(STATE_DIR, "seen_news.json") # 政策ウォッチ（新規）

# =========================================================
#  シリーズ①：論文 Q&A（学会の質疑形式・批判的トーン・各8分）
# =========================================================
# 検索クエリ（OpenAlex の全文検索）
TOPICS = [
    "urban heat island mitigation",
    "urban microclimate CFD simulation",
    "urban forest evapotranspiration cooling",
    "outdoor thermal comfort GIS remote sensing",
    "coupled indoor outdoor building energy microclimate",
    "urban canopy heat wave land surface temperature",
]
SINCE_DAYS = 3              # 「新着」とみなす直近日数（重複はseen.jsonで防ぐ）
PER_TOPIC = 20             # 各クエリ最大取得数
OPENALEX_MAILTO = os.environ.get("OPENALEX_MAILTO", "you@example.com")  # OpenAlex polite pool用
EPISODES_PER_RUN = 3      # 1エピソードの論文本数（不足分は高被引用で補充）
FALLBACK_YEARS = 4        # フォールバック：直近N年の高被引用論文

PAPER_MINUTES_PER = 8     # 1論文あたりの目安分数（24分 = 3本×8分）
PAPER_PREFIX = "🎓 論文Q&A"
PAPER_SEASON = 1
# 話者：発表者（著者役）＋ 討論者（批判的な査読者役）。(表示名, Geminiボイス)
PAPER_PRESENTER = ("発表者", "Charon")
PAPER_DISCUSSANT = ("討論者", "Leda")

# =========================================================
#  シリーズ②：政策ウォッチ（ニュース＋政策・アンカー＋アナリスト）
# =========================================================
# GDELT / RSS / Federal Register 用の検索語（英語でOK。GDELTは65言語横断）
NEWS_KEYWORDS = [
    "urban heat", "extreme heat policy", "heat wave city",
    "urban climate resilience", "building energy code climate",
    "cooling centers", "climate adaptation city",
]
# 信頼できるRSSフィード（description欄＝配信元要約を入力に使う。各URLは適宜調整）
NEWS_RSS_FEEDS = [
    "https://www.epa.gov/newsreleases/search/rss",
    "https://www.c40.org/news/feed/",
    "https://www.climatecentral.org/feed",
    "https://www.smartcitiesdive.com/feeds/news/",
]
NEWS_USE_GDELT = True
NEWS_USE_FEDERAL_REGISTER = True   # 米国の規則・告示（abstract＝公開要約を使用）
NEWS_TIMESPAN_HOURS = 36           # GDELT/RSSで遡る時間
NEWS_MAX_CANDIDATES = 45           # Claudeに渡す候補上限
NEWS_STORIES = 5                   # 1エピソードで扱う話題数
NEWS_MINUTES = 8                   # 目安分数（ニュースは短めが聴きやすい）
NEWS_PREFIX = "🏛️ 政策ウォッチ"
NEWS_SEASON = 2
NEWS_ANCHOR = ("アンカー", "Leda")
NEWS_ANALYST = ("アナリスト", "Charon")
