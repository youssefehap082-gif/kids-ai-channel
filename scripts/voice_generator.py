# scripts/voice_generator.py

import os
import logging
import requests
from gtts import gTTS
import tempfile
from pathlib import Path
from pydub import AudioSegment

log = logging.getLogger("voice_generator")

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVEN_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

TMP = Path(_file_).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)


# -----------------------------------------------------------
# 1) OpenAI TTS
# -----------------------------------------------------------
def tts_openai(text):
    try:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
        payload = {
            "model": "gpt-4o-mini-tts", 
            "input": text,
            "voice": "alloy"
        }

        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            raise Exception(r.text)

        out = TMP / "openai_voice.mp3"
        with open(out, "wb") as f:
            f.write(r.content)

        return out
    except Exception as e:
        log.error(f"OpenAI TTS failed: {e}")
        return None


# -----------------------------------------------------------
# 2) ElevenLabs TTS
# -----------------------------------------------------------
def tts_eleven(text, gender="male"):
    try:
        voice = "JBFqnCBsd6RMkjVDRZzb" if gender == "male" else "XB0fDUnXU5powFXDhCwa"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"

        headers = {
            "xi-api-key": ELEVEN_KEY,
            "Content-Type": "application/json"
        }

        payload = {"text": text, "voice_settings": {"stability": 0.3, "similarity_boost": 0.7}}

        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            raise Exception(r.text)

        out = TMP / "eleven_voice.mp3"
        with open(out, "wb") as f:
            f.write(r.content)

        return out
    except Exception as e:
        log.error(f"ElevenLabs TTS failed: {e}")
        return None


# -----------------------------------------------------------
# 3) Google gTTS fallback
# -----------------------------------------------------------
def tts_gtts(text):
    try:
        tts = gTTS(text=text, lang="en")
        out = TMP / "gtts_voice.mp3"
        tts.save(str(out))
        return out
    except Exception as e:
        log.error(f"gTTS failed: {e}")
        return None


# -----------------------------------------------------------
# MASTER FAILOVER – tries OpenAI → ElevenLabs → Google TTS
# -----------------------------------------------------------
def generate_voice_with_failover(text, gender="male"):
    log.info("Generating voice with failover...")

    # 1) OpenAI
    out = tts_openai(text)
    if out:
        return out

    # 2) ElevenLabs
    out = tts_eleven(text, gender)
    if out:
        return out

    # 3) gTTS
    out = tts_gtts(text)
    if out:
        return out

    raise RuntimeError("All TTS providers failed.")
