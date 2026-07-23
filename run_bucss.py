"""シリーズ③：BUCSS登壇者の論文（1エピソード＝登壇者1名を3本で深掘り・約24分）。
配信順は config.BUCSS_LECTURERS の並び＝キャリア接続の強い順。"""
import re
import datetime
from pipeline import config, bucss, select, script, tts, store


def main():
    # 既出論文（seen.json ＋ 配信済みエピソードの記録）は除外
    seen = set(store.load(config.SEEN_PATH, [])) | store.published_values("paper_ids")
    done_names = store.published_values("bucss_lecturers")

    lect = bucss.next_lecturer(done_names)
    if lect is None:
        print(f"BUCSS登壇者{len(config.BUCSS_LECTURERS)}名すべて配信済みです。終了。")
        return
    print(f"① 今回の登壇者: {lect['name']}（{lect['inst']}）")
    print(f"   {lect['note']}")

    papers = bucss.fetch_lecturer_papers(lect, seen)
    if not papers:
        print("この登壇者の論文候補が取得できませんでした。次回に持ち越します。終了。")
        return

    print("② 選別（研究プロファイルとの関連度順）")
    chosen = select.select_top(papers, k=config.BUCSS_PAPERS_PER_EP)
    for p in chosen:
        p["kind"] = "bucss"

    print("③④⑤ 台本＋音声（学会質疑形式・チャンク分割合成）")
    speakers = [config.PAPER_PRESENTER, config.PAPER_DISCUSSANT]
    segments, titles = [], []
    for i, p in enumerate(chosen):
        print(f"   - [被引用{p.get('cited_by_count', 0)}] {p['title'][:55]}")
        transcript = script.make_qa(p, intro=(i == 0))
        segments += tts.synth_long(transcript, speakers)
        titles.append(p["title"])

    today = datetime.date.today().isoformat()
    slug = re.sub(r"[^a-z0-9]+", "-", lect["name"].lower()).strip("-")
    fname = f"bucss-{slug}-{today}.mp3"   # 登壇者名を含め、同日再実行での上書きを防ぐ
    desc = (f"BUCSS登壇者 {lect['name']}（{lect['inst']}）の研究を批判的な質疑で読み解きます。\n"
            f"{lect['note']}\n\n今回の論文：\n"
            + "\n".join(f"・{t}" for t in titles))

    print("⑤b/⑥ MP3組み立て＋フィード再生成")
    dur = store.publish_episode(
        segments=segments,
        audio_dir=config.BUCSS_AUDIO_DIR, audio_subdir="bucss", fname=fname,
        title=f"{config.BUCSS_PREFIX}｜{lect['name']}（{lect['inst']}）",
        desc=desc, series=config.BUCSS_PREFIX, season=config.BUCSS_SEASON,
        date_iso=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        guid=f"bucss-{slug}",
        meta={"paper_ids": [p["id"] for p in chosen],
              "bucss_lecturers": [lect["name"]]},
    )

    seen.update(p["id"] for p in chosen)
    store.save(config.SEEN_PATH, sorted(seen))
    remaining = len(config.BUCSS_LECTURERS) - len(done_names) - 1
    print(f"完了：{fname}（{int(dur//60)}分{int(dur%60)}秒, {len(chosen)}本）残り登壇者 {remaining} 名")


if __name__ == "__main__":
    main()
