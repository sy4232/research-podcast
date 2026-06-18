"""シリーズ②：政策ウォッチ（GDELT+RSS+官報 → 批判的に選別 → アンカー＋アナリスト briefing）。"""
import datetime
from pipeline import config, news_fetch, news_script, tts, store


def main():
    seen = set(store.load(config.SEEN_NEWS_PATH, []))

    print("① 収集（ニュース/政策）"); cands = news_fetch.fetch_news(seen)
    if not cands:
        print("新規ニュースなし。終了。"); return

    print("② 選別・クラスタリング"); stories = news_script.select_stories(cands)
    if not stories:
        print("採用話題なし。終了。"); return
    for s in stories:
        print(f"   - {s['title'][:60]}")

    print("③ ブリーフィング台本")
    transcript = news_script.make_briefing(stories)

    print("④⑤ 音声（チャンク分割合成）")
    speakers = [config.NEWS_ANCHOR, config.NEWS_ANALYST]
    segments = tts.synth_long(transcript, speakers)

    today = datetime.date.today().isoformat()
    fname = f"news-{today}.mp3"
    desc = "今日の都市気候・政策ウォッチ：\n" + "\n".join(
        f"・{s['title']}（{', '.join(s['sources'])[:60]}）" for s in stories
    )

    print("⑤b/⑥ MP3組み立て＋フィード再生成")
    dur = store.publish_episode(
        segments=segments,
        audio_dir=config.NEWS_AUDIO_DIR, audio_subdir="news", fname=fname,
        title=f"{config.NEWS_PREFIX}｜{today}：{stories[0]['title'][:40]} ほか",
        desc=desc, series=config.NEWS_PREFIX, season=config.NEWS_SEASON,
        date_iso=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        guid=f"news-{fname}",
    )

    # 取り上げた話題のURLを既出として記録（毎日同じ報道の繰り返しを防ぐ）
    for s in stories:
        seen.update(u for u in s["urls"] if u)
    store.save(config.SEEN_NEWS_PATH, sorted(seen))
    print(f"完了：{fname}（{int(dur//60)}分{int(dur%60)}秒, {len(stories)}話題）")


if __name__ == "__main__":
    main()
