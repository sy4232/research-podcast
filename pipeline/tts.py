"""⑤ 音声化：Gemini マルチスピーカーTTS。長尺はチャンク分割＋リトライで安定生成。"""
import os
import re
import time
import base64
import requests
from . import config

ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{config.GEMINI_TTS_MODEL}:generateContent"
)


def _speaker_configs(speakers):
    return [
        {"speaker": name, "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}
        for (name, voice) in speakers
    ]


def _synth_once(transcript, speakers):
    """台本1チャンクを (pcm_bytes, rate) に変換。失敗時は例外。"""
    key = os.environ["GEMINI_API_KEY"]
    body = {
        "contents": [{"parts": [{
            "text": "次の日本語の会話を、自然な掛け合いで音声化してください:\n\n" + transcript
        }]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "multiSpeakerVoiceConfig": {"speakerVoiceConfigs": _speaker_configs(speakers)}
            },
        },
    }
    r = requests.post(
        ENDPOINT,
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json=body,
        timeout=240,
    )
    r.raise_for_status()
    parts = r.json()["candidates"][0]["content"]["parts"]
    inline = next((p["inlineData"] for p in parts if "inlineData" in p), None)
    if not inline:  # 稀にテキストが返ることがある
        raise RuntimeError("TTS returned no audio (text token)")
    pcm = base64.b64decode(inline["data"])
    m = re.search(r"rate=(\d+)", inline.get("mimeType", ""))
    return pcm, (int(m.group(1)) if m else 24000)


def _chunk_transcript(transcript, max_chars):
    """話者行（『名前: …』）の境界でチャンク分割。"""
    lines = [ln for ln in transcript.splitlines() if ln.strip()]
    chunks, cur, n = [], [], 0
    for ln in lines:
        if cur and n + len(ln) > max_chars:
            chunks.append("\n".join(cur))
            cur, n = [], 0
        cur.append(ln)
        n += len(ln)
    if cur:
        chunks.append("\n".join(cur))
    return chunks


def synth_long(transcript, speakers, max_chars=None, retries=None):
    """長い台本をチャンクごとに合成し、(pcm, rate) セグメントのリストを返す。"""
    max_chars = max_chars or config.TTS_CHUNK_CHARS
    retries = retries or config.TTS_RETRIES
    segments = []
    for chunk in _chunk_transcript(transcript, max_chars):
        for attempt in range(retries):
            try:
                segments.append(_synth_once(chunk, speakers))
                break
            except Exception as e:
                if attempt == retries - 1:
                    raise
                print(f"     [retry {attempt+1}/{retries-1}] TTS失敗: {e}")
                time.sleep(2 * (attempt + 1))
    return segments
