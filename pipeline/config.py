"""中央設定。両シリーズ（論文Q&A・政策ウォッチ）の設定をここに集約。"""
import os

# =========================================================
#  共通：研究プロファイル / モデル / 配信 / パス
# =========================================================
RESEARCH_PROFILE = (
    "Urban climate researcher focused on mitigating extreme heat and advancing sustainability through rigorous quantification of climate risk."
    "I integrate high-resolution CFD simulations with GIS, remote sensing, and data-driven methods to produce actionable insights that link urban form, infrastructure, and policy to resilient and equitable cities."
)

ANTHROPIC_MODEL = "claude-opus-4-8"   # 動かない時はここを変更。コスト優先なら "claude-sonnet-4-6"

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

# =========================================================
#  シリーズ⑤：地球・都市 気候モデリング講義（全15回・週1・日曜夜・テンポの良い掛け合い）
#  スケール階層（地球ESM ⇄ メソWRF/RCM ⇄ ローカルLES/CFD）＋観測＋統計/ML を、
#  CFD を先頭に据えて縦断する玄人向けシリーズ。全15回で自動終了。
# =========================================================
CLIMATE_MINUTES = 10
CLIMATE_PREFIX = "\U0001F30D 気候モデリング講義"   # 🌍
CLIMATE_SEASON = 5
CLIMATE_AUDIO_DIR = os.path.join(AUDIO_DIR, "climate")
# scripts/climate-01.md 等を置けば、その回は自動生成せず台本を“手書きで固定”できる（無ければ生成）。
CLIMATE_SCRIPT_DIR = os.path.join(REPO_ROOT, "scripts")
# 話者：ナビ（鋭い聞き手＝視聴者代表）＋ ハカセ（専門家）。(表示名, Geminiボイス)
CLIMATE_NAVI = ("ナビ", "Leda")
CLIMATE_HAKASE = ("ハカセ", "Charon")

CLIMATE_LECTURES = [
    {"no": 1, "title": "スケールの階層と“つなぎ目”",
     "scale": "全スケール横断（地球↔メソ↔ローカルの地図）",
     "topics": [
        "3つのスケールの守備範囲：地球ESM/GCM（〜100km）、メソWRF/RCM（〜数km）、ローカルLES/CFD（〜m）",
        "境界条件のバケツリレー：上のスケールが下のスケールの“入力”になるという入れ子構造",
        "つなぎ目＝ダウンスケーリング（力学的 vs 統計的）の役割と、そこで失われる情報",
        "グレーゾーン／terra incognita（1〜数km：対流も都市キャノピーも“解くでもパラメタライズでもない”中途半端）",
        "何がどのスケールで決まるか：総観場・都市ヒートアイランド・街区の風と暴露の切り分け",
        "実務の合言葉『いま自分はどのスケールを、どの解像度で解いているのか』",
     ],
     "hook": "シリーズ全体の“地図”。以降のCFD・観測・ダウンスケーリングすべての前提になる回。"},

    {"no": 2, "title": "都市CFD①：RANS vs LES、何を捨て何を解くか",
     "scale": "ローカル（建物・街区スケール）",
     "topics": [
        "RANS（アンサンブル平均・定常近似）と LES（渦を直接解く）の本質的な違い",
        "定常近似がいつ許され、いつ致命的か：剥離、非定常なキャニオン換気、間欠的乱流",
        "標準k-εが都市形状で持つ既知バイアスと、realizable/RNG/RSM などの修正の考え方",
        "計算コストの現実：LESは格子・時間刻みで桁違い、いつ払う価値があるか",
        "『何を知りたいか』で選ぶ：平均風か、ピーク暴露か、換気の間欠性か",
     ],
     "hook": "都市微気候の主戦場＝建物スケールの流れ。設定の一つ一つが“どの物理を捨てているか”を言語化する。"},

    {"no": 3, "title": "都市CFD②：メッシュ・境界条件・検証",
     "scale": "ローカル（建物・街区スケール）",
     "topics": [
        "格子設計のベストプラクティス（AIJ／COST 732系）：建物あたりセル数、鉛直第一層、領域とブロッケージ比",
        "流入境界条件と horizontal homogeneity 問題（入れた乱流が発達距離で崩れる）",
        "壁関数・粗度の扱いと、y+ の悩みどころ",
        "浮力・熱をどう入れるか：等温CFDの限界、Boussinesq近似、放射・熱収支との結合",
        "検証と感度解析：風洞・実測との比較、hit rate、『合った』だけでは不十分な理由、LES時間平均の収束",
     ],
     "hook": "CFDは“回れば正しい”ではない。再現性と検証がなければ、ただの綺麗な絵。"},

    {"no": 4, "title": "植生・水・潜熱 ― 蒸発散冷却の物理",
     "scale": "ローカル（表面〜キャノピー）",
     "topics": [
        "表面エネルギーバランス Q*=QH+QE+ΔQS+QF と、ボーエン比が日変化の位相を決める理由",
        "Penman-Monteith と、その都市適用での前提の崩れ",
        "気孔抵抗・キャノピー抵抗、土壌水分・飽差(VPD)による制御（“水がなければ冷えない”）",
        "樹冠の多孔質体モデル：葉面積密度(LAD)、抗力、乱流の生成・消散の追加項",
        "日射遮蔽(shading) と 蒸発散(ET) の寄与分離の難しさ、冷却の到達距離（移流・風速・樹林規模）",
     ],
     "hook": "『緑を増やせば涼しい』がどこまで本当か。ET冷却が効く条件・効かない条件を物理で詰める。"},

    {"no": 5, "title": "人体熱ストレスと屋内外連成",
     "scale": "ローカル→応用（人の暴露・建物）",
     "topics": [
        "平均放射温度(MRT)の算出：6方向放射計、球温度計、モデル推定の差と誤差",
        "熱指標の比較：UTCI・PET・WBGT が何を仮定し、どこで乖離するか",
        "固定点観測と個人暴露のギャップ、移動計測・ウェアラブルの可能性",
        "屋内外連成：ファサードの対流熱伝達率(CHTC)、微気候→建物負荷→屋内熱環境の連鎖",
        "『点/ピクセルの温度』から『人が受ける熱』へ飛躍する危うさ（次々回の伏線）",
     ],
     "hook": "最終的に効くのは“人が受ける熱”。指標の選び方ひとつで政策的な結論が変わる。"},

    {"no": 6, "title": "LCZとパラメタリゼーション ― スケールの橋",
     "scale": "ローカル⇄メソ（橋渡し）",
     "topics": [
        "Local Climate Zone(LCZ)/WUDAPT の思想と、クラス分けが捨象しているもの",
        "形態パラメータ：粗度長z0、ゼロ面変位d、平面充填率λp、前面積密度λf と推定の不確かさ",
        "都市キャノピーモデル（SLUCM/BEP/BEP-BEM）がメソに都市を“効かせる”仕組み",
        "サブグリッド平均化がいつ妥当で、いつ破綻するか",
        "Monin-Obukhov相似則が都市で破綻する理由（粗度層の非局所性、変位高さの不確実性）",
     ],
     "hook": "CFDの物理をそのまま全球には入れられない。“効かせ方”＝パラメタリゼーションが橋になる。"},

    {"no": 7, "title": "メソスケール① ― WRF/RCMと都市",
     "scale": "メソ（〜数km）",
     "topics": [
        "静力学 vs 非静力学、対流許容(convection-permitting)解像度の意味",
        "境界層スキーム（局所 vs 非局所、YSU/MYNN系）の含意",
        "ネスティング、スピンアップ、ナッジングの実務",
        "都市を入れる（WRF-urban）と地表面スキームとの結合",
        "グレーゾーン再訪：対流を“解く”でも“パラメタライズ”でもない中途半端さ",
     ],
     "hook": "都市ヒートアイランドを数十km四方で解く。ここでの選択が局地スケールの入力になる。"},

    {"no": 8, "title": "メソスケール② ― ダウンスケーリング（力学 vs 統計）",
     "scale": "メソ⇄ローカル（つなぎ目の本丸）",
     "topics": [
        "力学的ダウンスケーリング(RCMネスト)のコストと“付加価値(added value)”の議論",
        "統計的ダウンスケーリング：PP と MOS、変化量法(delta)、その前提",
        "バイアス補正(quantile mapping等)の落とし穴：定常性仮定、変数間の物理整合の破壊",
        "ML/超解像ダウンスケーリングの期待と検証の難しさ（transferability、分布外）",
        "『解像度を上げる ≠ 正しくなる』を見抜く目",
     ],
     "hook": "全球→街区の距離をどう埋めるか。研究の核心に最も近い回。"},

    {"no": 9, "title": "地球スケール① ― ESM/GCMと陸-大気結合",
     "scale": "地球（〜100km）",
     "topics": [
        "大気大循環の骨格と格子、力学コアと物理過程の分担",
        "陸面モデル（土壌水分・植生・表面エネルギーバランス）と大気の双方向結合",
        "パラメタリゼーション総覧：対流、雲、境界層、放射",
        "都市は“点”にすらならない現実と、それでも下流に効く理由",
        "CMIP と排出シナリオ(SSP)の位置づけ",
     ],
     "hook": "すべての境界条件の“親玉”。ここの不確実性が下流のすべてに効いてくる。"},

    {"no": 10, "title": "地球スケール② ― 熱・エアロゾル・雲・フィードバック",
     "scale": "地球（全球）",
     "topics": [
        "放射強制力と気候感度、雲フィードバックがなぜ最大の不確かさか",
        "エアロゾル-雲相互作用(ACI)が推定を難しくする理由",
        "全球の熱輸送・エネルギー収支と極端化のつながり",
        "検出・帰属(D&A)の基本的な考え方",
        "全球の温暖化が地域の極端熱にどう“降りてくる”か",
     ],
     "hook": "なぜ気候感度は数十年決着しないのか。不確実性の“出どころ”を解剖する。"},

    {"no": 11, "title": "観測① ― 熱リモートセンシングとLSTリトリーバル",
     "scale": "観測（全スケール横断）",
     "topics": [
        "センサの時空間トレードオフ：Landsat/MODIS/GOES/ECOSTRESS が“何を”“いつ”見るか",
        "LSTリトリーバル：大気補正、split-window、放射率の推定",
        "指向性放射率・角度異方性が衛星LSTに与えるバイアス",
        "雲・欠損とギャップフィリング、昼夜・観測時刻の違い",
        "そもそも衛星が見ているのは“表面の皮膚温(skin temperature)”であること",
     ],
     "hook": "衛星の温度は便利だが誤解の温床。まず“何を見ているのか”を正確に。"},

    {"no": 12, "title": "観測② ― LST≠気温、surface-to-society",
     "scale": "観測→応用（解釈の要）",
     "topics": [
        "LST（表面温度）と Ta（気温）と Tmrt（放射）の物理的な違い",
        "SUHI（表面ヒートアイランド）と AUHI（気温ヒートアイランド）がずれる理由",
        "『cooling pixels ≠ cooling people』：表面が冷えても人が涼しいとは限らない",
        "LSTが正当に使える場面（表面エネルギー収支、モデルの入力/検証、表面介入の評価、放射/MRT寄与）",
        "LSTを使うべきでない場面（人口の熱暴露・ハザードの代理）と、実務での正しい主張の仕方",
     ],
     "hook": "リモセン研究者が最も足をすくわれる論点。LSTの“使いどころ”を正面から扱う。"},

    {"no": 13, "title": "観測③ ― その場観測とフラックス",
     "scale": "観測（点〜フットプリント）",
     "topics": [
        "フラックスタワー：渦相関法、顕熱/潜熱の分配、フットプリントの考え方",
        "都市での相似則の破綻と、観測そのものの難しさ",
        "クラウドソーシング・移動観測・オポチュニスティックセンシングと品質管理",
        "観測ネットワークの設計：代表性、設置バイアス",
        "モデル検証における“観測側の不確実性”を忘れない",
     ],
     "hook": "モデルを裁く“物差し”にも誤差がある。観測を鵜呑みにしないための回。"},

    {"no": 14, "title": "統計・ML・因果・不確実性",
     "scale": "横断（手法論）",
     "topics": [
        "統計/MLの位置づけ：エミュレーション、超解像、パラメタリゼーション代替",
        "因果推論（DiD等）で介入効果を測る作法と、交絡の扱い",
        "不確実性の定量化：アンサンブル、UQ、感度解析",
        "検証指標の選び方と『良く見える』罠（R²だけでは足りない）",
        "データ駆動と物理のハイブリッド（physics-informed）の勘所",
     ],
     "hook": "『R²が高い』で満足しない。何を測れば意思決定に耐えるのかを詰める。"},

    {"no": 15, "title": "統合 ― デジタル・アーバン・クライメイト・ツイン",
     "scale": "全スケール統合（地球→メソ→ローカル＋観測＋同化）",
     "topics": [
        "全スケール＋観測＋データ同化を束ねる思想と、その現実",
        "デジタルツインの誇大広告と実像の切り分け：何が可能で、何がまだ無理か",
        "計算・同化・検証のボトルネック",
        "科学→政策の翻訳：不確実性を保ったまま意思決定に渡す作法",
        "シリーズ総括と、研究者としての立ち位置",
     ],
     "hook": "全部つないだら何ができるのか。広げた“地図”を一枚に畳んで完結する回。"},
]
