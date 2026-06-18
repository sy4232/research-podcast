"""⑤ 音声化：Gemini マルチスピーカーTTS。長尺はチャンク分割し、
レート制限(429)対策として呼び出し間隔のスロットリング＋Retry-After準拠のバックオフを行う。"""
import os
import re
import time
import base64
import random
import requests
from . import config

ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{config.GEMINI_TTS_MODEL}:generateContent"
)

_last_call = [0.0]   # 直近のTTS呼び出し時刻（プロセス内で共有しRPMを抑える）


def _throttle():
    wait = config.TTS_MIN_INTERVAL_SEC - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)


def _speaker_configs(speakers):
    return [
        {"speaker": name, "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}
        for (name, voice) in speakers
    ]


def _synth_once(transcript, speakers):
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
    if not inline:
        raise RuntimeError("TTS returned no audio (text token)")
    pcm = base64.b64decode(inline["data"])
    m = re.search(r"rate=(\d+)", inline.get("mimeType", ""))
    return pcm, (int(m.group(1)) if m else 24000)


def _retry_after(resp, attempt):
    """429時の待機秒。Retry-Afterヘッダ→本文retryDelay→指数バックオフの順で決定。"""
    if resp is not None:
        ra = resp.headers.get("Retry-After")
        if ra:
            try:
                return float(ra)
            except ValueError:
                pass
        try:
            for d in resp.json().get("error", {}).get("details", []):
                rd = d.get("retryDelay")
                if rd:
                    return float(str(rd).rstrip("s"))
        except Exception:
            pass
    return config.TTS_BACKOFF_BASE * (2 ** attempt) + random.uniform(0, 3)


def _chunk_transcript(transcript, max_chars):
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
                _throttle()
                seg = _synth_once(chunk, speakers)
                _last_call[0] = time.time()
                segments.append(seg)
                break
            except requests.HTTPError as e:
                _last_call[0] = time.time()
                code = getattr(e.response, "status_code", None)
                if attempt == retries - 1:
                    if code == 429:
                        raise RuntimeError(
                            "Gemini TTSのレート制限(429)が解消しませんでした。"
                            "無料枠の分間上限(RPM)か日次上限(RPD)に達しています。"
                            "config.TTS_MIN_INTERVAL_SEC を増やすか、AI Studioで課金を有効化（上位ティア）してください。"
                        ) from e
                    raise
                delay = _retry_after(e.response, attempt) if code == 429 else 2 * (attempt + 1)
                print(f"     [{code}] {delay:.0f}秒待機して再試行 ({attempt+1}/{retries-1})")
                time.sleep(delay)
            except Exception as e:
                _last_call[0] = time.time()
                if attempt == retries - 1:
                    raise
                print(f"     [retry {attempt+1}/{retries-1}] TTS失敗: {e}")
                time.sleep(2 * (attempt + 1))
    return segments
