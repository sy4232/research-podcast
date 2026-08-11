"""シリーズ⑤：地球・都市 気候モデリング講義（全15回で完結）。
配信済みの回はスキップし、15回終了後は自動停止（何も配信せず終了）。"""
import datetime
from pipeline import config, climate, tts, store


def main():
    done = {int(n) for n in store.published_values("climate_numbers")}
    spec = climate.next_climate(done)
    if spec is None:
        print(f"気候モデリング講義シリーズ（全{len(config.CLIMATE_LECTURES)}回）は完結済みです。終了。")
        return

    total = len(config.CLIMATE_LECTURES)
    print(f"① 第{spec['no']}回／全{total}回：{spec['title']}")

    print("② 台本生成")
    transcript = climate.make_climate(spec)

    print("③ 音声（チャンク分割合成）")
    speakers = [config.CLIMATE_NAVI, config.CLIMATE_HAKASE]
    segments = tts.synth_long(transcript, speakers)

    today = datetime.date.today().isoformat()
    fname = f"climate-{spec['no']:02d}-{today}.mp3"
    desc = (f"地球・都市 気候モデリング講義 第{spec['no']}回／全{total}回\n"
            f"{spec['hook']}\n\n扱う内容：\n"
            + "\n".join(f"・{t}" for t in spec["topics"]))

    print("④ MP3組み立て＋フィード再生成")
    dur = store.publish_episode(
        segments=segments,
        audio_dir=config.CLIMATE_AUDIO_DIR, audio_subdir="climate", fname=fname,
        title=f"{config.CLIMATE_PREFIX} 第{spec['no']}回／全{total}回：{spec['title']}",
        desc=desc, series=config.CLIMATE_PREFIX, season=config.CLIMATE_SEASON,
        date_iso=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        guid=f"climate-{spec['no']:02d}",
        meta={"climate_numbers": [spec["no"]]},
    )
    remaining = total - len(done) - 1
    tail = "シリーズ完結です。" if remaining <= 0 else f"残り {remaining} 回。"
    print(f"完了：{fname}（{int(dur//60)}分{int(dur%60)}秒）{tail}")


if __name__ == "__main__":
    main()
