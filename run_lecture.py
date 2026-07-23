"""シリーズ④：上級・都市微気候 講義（全5回で完結）。配信済みの回はスキップし、5回終了後は自動停止。"""
import datetime
from pipeline import config, lecture, tts, store


def main():
    done = {int(n) for n in store.published_values("lecture_numbers")}
    spec = lecture.next_lecture(done)
    if spec is None:
        print(f"講義シリーズ（全{len(config.LECTURES)}回）は完結済みです。終了。")
        return

    total = len(config.LECTURES)
    print(f"① 第{spec['no']}回／全{total}回：{spec['title']}")

    print("② 台本生成")
    transcript = lecture.make_lecture(spec)

    print("③ 音声（チャンク分割合成）")
    speakers = [config.LECTURER_VOICE, config.STUDENT_VOICE]
    segments = tts.synth_long(transcript, speakers)

    today = datetime.date.today().isoformat()
    fname = f"lecture-{spec['no']:02d}-{today}.mp3"
    desc = (f"上級・都市微気候 講義シリーズ 第{spec['no']}回／全{total}回\n"
            f"{spec['hook']}\n\n扱う内容：\n"
            + "\n".join(f"・{t}" for t in spec["topics"]))

    print("④ MP3組み立て＋フィード再生成")
    dur = store.publish_episode(
        segments=segments,
        audio_dir=config.LECTURE_AUDIO_DIR, audio_subdir="lecture", fname=fname,
        title=f"{config.LECTURE_PREFIX} 第{spec['no']}回／全{total}回：{spec['title']}",
        desc=desc, series=config.LECTURE_PREFIX, season=config.LECTURE_SEASON,
        date_iso=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        guid=f"lecture-{spec['no']:02d}",
        meta={"lecture_numbers": [spec["no"]]},
    )
    remaining = total - len(done) - 1
    tail = "シリーズ完結です。" if remaining <= 0 else f"残り {remaining} 回。"
    print(f"完了：{fname}（{int(dur//60)}分{int(dur%60)}秒）{tail}")


if __name__ == "__main__":
    main()
