# 都市気候リサーチ・ダイジェスト 🎙️

自分の研究に関連する最新論文を **毎週自動で収集 → Claudeで選別・日本語の対話台本化 → Gemini多声TTSで音声化 → GitHub Pages の RSS で配信** するパイプライン。iPhoneの「ポッドキャスト」アプリで購読すれば、放置で毎週エピソードが増えます。

```
収集(OpenAlex) → 選別(Claude) → 台本(Claude) → 音声(Gemini TTS) → MP3 → RSS(GitHub Pages)
                                                          ↑ すべて GitHub Actions の cron で自動
```

## セットアップ（10分）

1. **このリポジトリを自分のGitHubに作成**（private可。Pagesを使うなら public が簡単）。
2. **GitHub Pages を有効化**
   Settings → Pages → Source = *Deploy from a branch* → Branch = `main` / フォルダ `/docs`。
   公開URL（例 `https://<ユーザー名>.github.io/research-podcast`）を控える。
3. **Secrets を登録**（Settings → Secrets and variables → Actions → *Secrets*）
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY`（Google AI Studio で取得）
4. **Variables を登録**（同じ画面の *Variables* タブ）
   - `PAGES_BASE_URL` = 手順2のURL
   - `OPENALEX_MAILTO` = 自分のメール（APIの優先キュー用）
5. **研究テーマを編集**：`pipeline/config.py` の `RESEARCH_PROFILE` と `TOPICS` を自分に合わせる。
6. **動作確認**：Actions タブ → *weekly-research-podcast* → *Run workflow*（手動実行）。
   成功すると `docs/audio/ep-YYYY-MM-DD.mp3` と `docs/podcast.xml` が増える。

## iPhoneで購読

Apple「ポッドキャスト」アプリ →「ライブラリ」→ 右上 … →「番組をURLで追加」→
`https://<ユーザー名>.github.io/research-podcast/podcast.xml` を入力。
以後、毎週新エピソードが自動で届きます。Overcast / Pocket Casts でも同じURLでOK。

## カスタマイズ早見表（`pipeline/config.py`）

| やりたいこと | 変える場所 |
|---|---|
| 研究テーマ・検索語 | `RESEARCH_PROFILE`, `TOPICS` |
| 1回の本数 | `EPISODES_PER_RUN` |
| 配信頻度 | `.github/workflows/weekly.yml` の `cron` |
| 話者の声 | `HOST_A_VOICE`, `HOST_B_VOICE`（Gemini TTSのボイス名） |
| コスト削減 | `ANTHROPIC_MODEL = "claude-sonnet-4-6"` |
| TTSを別社に差し替え | `pipeline/tts.py` の `synth_dialogue` だけ置換（戻り値は `(pcm_bytes, rate)`） |

## コスト感
週3本でClaude＋Gemini TTS 合わせて月 数ドル程度。GitHub Actions / Pages は無料枠内。

## 仕組みメモ
- 重複防止：処理済みのOpenAlex IDを `state/seen.json` に記録。
- 配信状態：`state/episodes.json` が唯一の真実。毎回ここから `podcast.xml` と `index.html` を再生成。
- 音声：Gemini TTSの出力は生PCM。`pipeline/audio.py` でWAV化→ffmpegでMP3化し、論文セグメントを無音を挟んで連結。
