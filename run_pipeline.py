"""シリーズ①：論文 Q&A（批判的質疑・各8分・3本＝約24分）。GitHub Actions から実行。"""
import datetime
from pipeline import config, fetch, select, script, tts, store


def main():
    # 重複防止：seen.json と「配信済みエピソードに記録された論文ID」の両方を除外対象にする
    seen = set(store.load(config.SEEN_PATH, [])) | store.published_values("paper_ids")
    target = config.EPISODES_PER_RUN

    print("① 収集（新着）"); new_papers = fetch.fetch_recent(seen)
    print("② 選別（新着）")
    chosen = select.select_top(new_papers, k=target) if new_papers else []
    for p in chosen:
        p["kind"] = "new"

    if len(chosen) < target:                       # 新着が足りなければ高被引用で補充
        need = target - len(chosen)
        print(f"① 収集（フォールバック：高被引用を{need}本）")
        exclude = set(seen) | {p["id"] for p in chosen}
        cited = fetch.fetch_top_cited(exclude, need)
        print("② 選別（フォールバック）")
        picked = select.select_top(cited, k=need) if cited else []
        for p in picked:
            p["kind"] = "highly_cited"
        chosen += picked

    if not chosen:
        print("候補なし。終了。"); return

    print("③④⑤ 台本＋音声（チャンク分割合成）")
    speakers = [config.PAPER_PRESENTER, config.PAPER_DISCUSSANT]
    segments, titles = [], []
    for i, p in enumerate(chosen):
        tag = "新着" if p.get("kind") == "new" else f"被引用{p.get('cited_by_count', 0)}"
        print(f"   - [{tag}] {p['title'][:55]}")
        transcript = script.make_qa(p, intro=(i == 0))
        segments += tts.synth_long(transcript, speakers)
        titles.append(p["title"])

    today = datetime.date.today().isoformat()
    fname = f"papers-{today}.mp3"

    def _line(p):
        if p.get("kind") == "highly_cited":
            return f"・[注目・被引用{p.get('cited_by_count', 0)}] {p['title']}"
        return f"・[新着] {p['title']}"

    print("⑤b/⑥ MP3組み立て＋フィード再生成")
    dur = store.publish_episode(
        segments=segments,
        audio_dir=config.PAPER_AUDIO_DIR, audio_subdir="papers", fname=fname,
        title=(f"{config.PAPER_PREFIX}｜{today}：{titles[0][:34]} ほか{len(titles)-1}本"
               if len(titles) > 1 else f"{config.PAPER_PREFIX}｜{today}：{titles[0][:44]}"),
        desc="批判的な質疑応答で読み解く今回の論文：\n" + "\n".join(_line(p) for p in chosen),
        series=config.PAPER_PREFIX, season=config.PAPER_SEASON,
        date_iso=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        guid=f"papers-{fname}",
        meta={"paper_ids": [p["id"] for p in chosen]},
    )

    seen.update(p["id"] for p in chosen)
    store.save(config.SEEN_PATH, sorted(seen))
    print(f"完了：{fname}（{int(dur//60)}分{int(dur%60)}秒, {len(chosen)}本）")


if __name__ == "__main__":
    main()
