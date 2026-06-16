"""⑤b 音声組み立て：複数セグメントのPCMを連結→WAV→MP3。所要時間(秒)も返す。"""
import os
import wave
import struct
import subprocess
from . import config


def _silence(seconds, rate):
    return b"\x00\x00" * int(seconds * rate)  # 16bit mono の無音


def build_episode_mp3(segments, out_mp3_path):
    """
    segments: [(pcm_bytes, rate), ...]
    すべて同一サンプルレート前提（Gemini TTSは一定）。MP3を書き出し duration_sec を返す。
    """
    rate = segments[0][1]
    gap = _silence(config.AUDIO_GAP_SEC, rate)
    pcm = b""
    for i, (data, _) in enumerate(segments):
        if i:
            pcm += gap
        pcm += data

    wav_path = out_mp3_path.replace(".mp3", ".wav")
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)      # 16bit
        w.setframerate(rate)
        w.writeframes(pcm)

    # ffmpeg で MP3 へ（GitHub Actions では apt で ffmpeg を入れておく）
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
         "-codec:a", "libmp3lame", "-qscale:a", "4", out_mp3_path],
        check=True,
    )
    os.remove(wav_path)

    duration_sec = len(pcm) / 2 / rate
    return duration_sec
