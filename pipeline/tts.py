"""⑤ 音声化：Gemini マルチスピーカーTTS で台本→生PCM音声（base64デコード済みbytes）。"""
import os
import re
import base64
import requests
from . import config

ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{config.GEMINI_TTS_MODEL}:generateContent"
)


def synth_dialogue(transcript):
    """『あかり: …/けんた: …』形式の台本を1ファイルぶんの (pcm_bytes, sample_rate) に変換。"""
    key = os.environ["GEMINI_API_KEY"]
    body = {
        "contents": [{"parts": [{
            "text": "次の日本語の会話を、自然な掛け合いで音声化してください:\n\n" + transcript
        }]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "multiSpeakerVoiceConfig": {
                    "speakerVoiceConfigs": [
                        {"speaker": config.HOST_A_NAME,
                         "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": config.HOST_A_VOICE}}},
                        {"speaker": config.HOST_B_NAME,
                         "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": config.HOST_B_VOICE}}},
                    ]
                }
            },
        },
    }
    r = requests.post(
        ENDPOINT,
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json=body,
        timeout=180,
    )
    r.raise_for_status()
    part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
    pcm = base64.b64decode(part["data"])
    m = re.search(r"rate=(\d+)", part.get("mimeType", ""))
    rate = int(m.group(1)) if m else 24000
    return pcm, rate
