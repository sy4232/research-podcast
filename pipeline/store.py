"""共有状態（episodes.json）とエピソード追加・フィード再生成の共通処理。"""
import os
import json
from . import config, feed, audio


def load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def published_values(key):
    """過去の全エピソードから、指定キー（例 'paper_ids' / 'story_urls'）の値を集合で返す。
    episodes.json は購読フィードの元データとして確実に永続するため、重複防止の信頼できる土台になる。"""
    vals = set()
    for ep in load(config.EPISODES_PATH, []):
        vals.update(ep.get(key, []) or [])
    return vals


def publish_episode(segments, audio_dir, audio_subdir, fname, title, desc,
                    series, season, date_iso, guid, meta=None):
    """音声を書き出し、共有 episodes.json に追記して単一フィードを再生成する。"""
    os.makedirs(audio_dir, exist_ok=True)
    out_path = os.path.join(audio_dir, fname)
    duration = audio.build_episode_mp3(segments, out_path)

    ep = {
        "title": title,
        "desc": desc,
        "date": date_iso,
        "audio_rel": f"audio/{audio_subdir}/{fname}",
        "file": fname,
        "bytes": os.path.getsize(out_path),
        "duration": duration,
        "guid": guid,
        "series": series,
        "season": season,
    }
    if meta:
        ep.update(meta)   # 例: paper_ids / story_urls（重複防止の記録）
    episodes = load(config.EPISODES_PATH, [])
    episodes.insert(0, ep)
    # 新しい順に整列（両シリーズ混在のため日付でソート）
    episodes.sort(key=lambda e: e.get("date", ""), reverse=True)
    feed.write_feed(episodes)
    feed.write_index(episodes)
    save(config.EPISODES_PATH, episodes)
    return duration
