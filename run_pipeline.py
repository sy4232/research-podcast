"""全体を回すエントリポイント。GitHub Actions から `python run_pipeline.py` で実行。"""
import os
import json
import datetime
from pipeline import config, fetch, select, script, tts, audio, feed


def _load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def _save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    os.makedirs(config.AUDIO_DIR, exist_ok=True)
    seen = set(_load(config.SEEN_PATH, []))
    episodes = _load(config.EPISODES_PATH, [])  # 新しい順

    target = config.EPISODES_PER_RUN

    print("① 収集（新着）"); new_papers = fetch.fetch_recent(seen)
    print("② 選別（新着）")
    chosen = select.select_top(new_papers, k=target) if new_papers else []
    for p in chosen:
        p["kind"] = "new"

    # 新着が target 本に満たなければ、直近FALLBACK_YEARS年の高被引用論文で補充
    if len(chosen) < target:
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
        print("候補なし（新着も高被引用も0）。終了。"); return

    print("③④⑤ 台本＋音声")
    segments, titles = [], []
    for i, p in enumerate(chosen):
        tag = "新着" if p.get("kind") == "new" else f"被引用{p.get('cited_by_count', 0)}"
        print(f"   - [{tag}] {p['title'][:55]}")
        transcript = script.make_dialogue(p, intro=(i == 0))
        pcm, rate = tts.synth_dialogue(transcript)
        segments.append((pcm, rate))
        titles.append(p["title"])

    today = datetime.date.today().isoformat()
    fname = f"ep-{today}.mp3"
    out_path = os.path.join(config.AUDIO_DIR, fname)
    print("⑤b MP3組み立て")
    duration = audio.build_episode_mp3(segments, out_path)

    def _line(p):
        if p.get("kind") == "highly_cited":
            return f"・[注目・被引用{p.get('cited_by_count', 0)}] {p['title']}"
        return f"・[新着] {p['title']}"

    ep = {
        "title": f"{today} のダイジェスト：{titles[0][:40]} ほか{len(titles)-1}本"
                 if len(titles) > 1 else f"{today}：{titles[0][:50]}",
        "desc": "今回の論文：\n" + "\n".join(_line(p) for p in chosen),
        "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "file": fname,
        "bytes": os.path.getsize(out_path),
        "duration": duration,
        "guid": fname,
    }
    episodes.insert(0, ep)

    print("⑥ RSS / index 生成")
    feed.write_feed(episodes)
    feed.write_index(episodes)

    seen.update(p["id"] for p in chosen)
    _save(config.SEEN_PATH, sorted(seen))
    _save(config.EPISODES_PATH, episodes)
    print(f"完了：{fname}（{int(duration//60)}分{int(duration%60)}秒, {len(chosen)}本）")


if __name__ == "__main__":
    main()
