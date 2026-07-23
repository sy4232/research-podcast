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
BUCSS_AUDIO_DIR = os.path.join(AUDIO_DIR, "bucss")
LECTURE_AUDIO_DIR = os.path.join(AUDIO_DIR, "lecture")
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

# =========================================================
#  シリーズ③：BUCSS登壇者の論文（週2本・1エピソード＝1名を深掘り）
#  Bochum Urban Climate Summer School (Ruhr-Universitat Bochum) 講師陣。
#  ★並び順＝配信順。Seanのキャリア（CFD微気候／ET冷却／屋内外連成／GIS・RS／
#    政策translation／US就活）との接続が強い順。並べ替えれば配信順が変わる。
# =========================================================
BUCSS_LECTURERS = [
    {"name": "Ariane Middel",         "inst": "Arizona State University",         "note": "都市形態と人体熱暴露・微気候シミュレーション・urban climate informatics／IAUC会長・米国"},
    {"name": "Negin Nazarian",        "inst": "University of New South Wales",    "note": "高解像度都市気候モデリング・都市キャノピーパラメタリゼーション・熱と風／CFD出身・IPCC AR7"},
    {"name": "Gert-Jan Steeneveld",   "inst": "Wageningen University",           "note": "都市微気候・PALM4U/ENVI-met/WRF・屋内気候観測・科学と政策の橋渡し"},
    {"name": "Ferdinand Briegel",     "inst": "Karlsruhe Institute of Technology","note": "歩行者熱ストレスの高解像度モデリング・メソ〜マイクロのハイブリッド化"},
    {"name": "Charles Pierce",        "inst": "University of Bern",              "note": "機械工学・CFD出身、都市風モデリングと熱ストレスのダウンスケーリング"},
    {"name": "Fred Meier",            "inst": "Technische Universitat Berlin",   "note": "都市微気候の熱リモートセンシング・植生の役割・微/中規模モデル"},
    {"name": "Andreas Christen",      "inst": "University of Freiburg",          "note": "都市エネルギーバランス・乱流フラックス観測（潜熱/顕熱の分配）"},
    {"name": "Gerald Mills",          "inst": "University College Dublin",       "note": "都市気候の計画・設計への翻訳・都市緑化・LCZ/WUDAPT"},
    {"name": "Matthias Demuzere",     "inst": "Ghent University",                "note": "LCZ・世界銀行の都市熱レジリエンス・heat action planning"},
    {"name": "Benjamin Bechtel",      "inst": "Ruhr-University Bochum",          "note": "都市リモートセンシング・都市表面のLCZ特性評価"},
    {"name": "Panagiotis Sismanidis", "inst": "Ruhr-University Bochum",          "note": "LST時系列解析・統計的ダウンスケーリング・熱と健康"},
    {"name": "Simone Kotthaus",       "inst": "Ecole Polytechnique",             "note": "都市境界層観測・熱と大気汚染・都市緑化"},
    {"name": "Lara van der Linden",   "inst": "Ruhr-University Bochum",          "note": "PALMによるstreet-level微気候数値モデリングと地理データ品質"},
    {"name": "Daniel Fenner",         "inst": "Technische Universitat Berlin",   "note": "都市境界層・熱波・クラウドソーシング観測"},
    {"name": "Luise Wolf",            "inst": "Ruhr-University Bochum",          "note": "AI/データサイエンスによる都市熱モデリングと熱快適性"},
    {"name": "Sara Top",              "inst": "Ghent University",                "note": "機械学習による高解像度都市気候データ・MetObs-toolkit"},
    {"name": "Arjan Droste",          "inst": "Delft University of Technology",  "note": "都市水文気象・opportunistic sensing"},
    {"name": "Lesley De Cruz",        "inst": "Royal Meteorological Institute",  "note": "AI気象予測・ナウキャスティング"},
    {"name": "Jonas Kittner",         "inst": "Ruhr-University Bochum",          "note": "スマートホーム気象データのクラウドソーシング"},
    {"name": "Sorin Cheval",          "inst": "European Meteorological Society", "note": "欧州気象学会"},
]
BUCSS_PAPERS_PER_EP = 3      # 1エピソードで扱う本数（3本×8分＝約24分）
BUCSS_PREFIX = "\U0001F3AF BUCSS登壇者"
BUCSS_SEASON = 3

# =========================================================
#  シリーズ④：上級・都市微気候 講義（全5回で完結・週2本）
# =========================================================
LECTURE_MINUTES = 13
LECTURE_PREFIX = "\U0001F4DA 上級講義"
LECTURE_SEASON = 4
LECTURER_VOICE = ("講師", "Charon")
STUDENT_VOICE = ("受講生", "Leda")

LECTURES = [
    {"no": 1, "title": "都市境界層とスケールの物理",
     "topics": [
        "都市キャノピー層(UCL)・粗度層(RSL)・慣性層・都市境界層(UBL)の鉛直構造と、各層で成り立つ仮定",
        "Monin-Obukhov相似則が都市で破綻する理由（粗度層内の非局所性、分散応力、変位高さの不確実性）",
        "形態パラメータ：粗度長z0、ゼロ面変位d、平面充填率λp、前面積密度λf と推定法の不確かさ",
        "Local Climate Zone(LCZ)の思想と限界：クラス分けが何を捨象しているか",
        "スケールの整合：どの現象をどの解像度で解くべきか（メソ／マイクロ／CFDの守備範囲）",
     ],
     "hook": "『いま自分はどのスケールを解いているのか』の自覚が、以降のCFD設定・観測比較・LST解釈すべての前提になる。"},
    {"no": 2, "title": "表面エネルギーバランスと放射",
     "topics": [
        "都市の表面エネルギーバランス：純放射Q*、顕熱QH、潜熱QE、蓄熱ΔQS、人工排熱QF の各項",
        "蓄熱フラックスの扱い（OHM等のヒステリシス）と、それが日変化の位相を決める理由",
        "キャニオン内の放射トラップ：Sky View Factor、多重反射、長波交換の幾何依存性",
        "LST(表面温度)とTa(気温)の決定的な違い：衛星が見ているものは何か、なぜSUHIとAUHIがずれるのか",
        "指向性放射率・角度異方性が衛星LSTに与えるバイアス",
     ],
     "hook": "リモートセンシング研究で最も誤解されやすいLSTとTaの乖離を、エネルギーバランスの言葉で厳密に整理する。"},
    {"no": 3, "title": "CFDによる都市微気候シミュレーション",
     "topics": [
        "RANSとLESの選択：定常近似がいつ許され、いつ致命的か（剥離、非定常渦、キャニオン換気）",
        "乱流モデルの含意：標準k-εが都市形状で持つ既知のバイアスと修正の考え方",
        "格子設計のベストプラクティス（AIJ／COST 732系）：建物あたりセル数、鉛直第一層、計算領域とブロッケージ比",
        "流入境界条件：鉛直プロファイルの整合性とhorizontal homogeneity問題",
        "検証と感度解析：風洞・実測との比較指標、hit rate、『合った』だけでは不十分な理由",
        "浮力と熱をどう入れるか：等温CFDの限界と放射・熱収支との結合",
     ],
     "hook": "Fluent等での実務に直結する回。設定の一つ一つが、どの物理を捨てているかを言語化する。"},
    {"no": 4, "title": "植生・水・潜熱 ― 蒸発散冷却の物理",
     "topics": [
        "Penman-Monteithと、その都市適用における前提の崩れ",
        "気孔抵抗・キャノピー抵抗と、土壌水分・飽差(VPD)による制御（水がなければ冷えない）",
        "葉面積密度(LAD)と樹冠の多孔質体モデル：抗力係数、乱流の生成・消散の追加項",
        "顕熱／潜熱の分配（ボーエン比）が都市形態と灌漑でどう変わるか",
        "冷却の到達距離を決める要因：移流、風速、湿度、樹林規模",
        "日射遮蔽(shading)と蒸発散(ET)の寄与分離：測定・モデル双方での難しさ",
     ],
     "hook": "博士研究の核心と重なる回。ET冷却がいつ効き、いつ効かないかを物理から詰める。"},
    {"no": 5, "title": "人体熱ストレスと屋内外連成 ― 応用と政策への翻訳",
     "topics": [
        "平均放射温度(MRT)の算出：6方向放射計、球温度計、モデル推定の差と誤差",
        "熱指標の比較：UTCI、PET、WBGTが何を仮定し、どこで乖離するか",
        "個人暴露と固定点観測のギャップ、移動計測・ウェアラブルの可能性",
        "屋内外連成：ファサードの対流熱伝達率(CHTC)、微気候→建物負荷→屋内熱環境の連鎖と未解決問題",
        "緩和策の評価：冷却効果をどの指標・どの空間スケールで測れば政策判断に耐えるか",
        "科学から政策へ：不確実性を保ったまま意思決定に渡す作法",
     ],
     "hook": "『屋外CFDと屋内熱環境の連成』という知識ギャップを、シリーズの締めとして正面から扱う。"},
]
