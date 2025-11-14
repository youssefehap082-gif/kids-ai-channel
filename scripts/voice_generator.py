import os
from pathlib import Path
from gtts import gTTS
from moviepy.editor import AudioFileClip
import requests
import tempfile

TMP = Path(__file__).resolve().parent / "tmp_voice"
TMP.mkdir(exist_ok=True)

# ============================================================
# 1) Google gTTS (Always available fallback)
# ============================================================
def tts_google(text, gender="male"):
    try:
        tts = gTTS(text=text, lang="en")
        out = TMP / "gtts_voice.mp3"
        tts.save(out)
        return out
    except Exception as e:
        raise RuntimeError(f"gTTS failed: {e}")

# ============================================================
# 2) OpenAI TTS Backup
# ============================================================
def tts_openai(text, gender="male"):
    api = os.getenv("OPENAI_API_KEY")
    if not api:
        raise RuntimeError("OPENAI_API_KEY not set")

    url = "https://api.openai.com/v1/audio/speech"
    voice = "alloy" if gender == "male" else "verse"

    payload = {
        "model": "gpt-4o-mini-tts",
        "voice": voice,
        "input": text
    }

    out = TMP / "openai_voice.mp3"
    try:
        r = requests.post(url, json=payload, headers={
            "Authorization": f"Bearer {api}"
        })
        if r.status_code != 200:
            raise RuntimeError(r.text)

        with open(out, "wb") as f:
            f.write(r.content)

        return out
    except Exception as e:
        raise RuntimeError(f"OpenAI TTS failed: {e}")

# ============================================================
# 3) ElevenLabs Backup
# ============================================================
def tts_elevenlabs(text, gender="male"):
    api = os.getenv("ELEVEN_API_KEY")
    if not api:
        raise RuntimeError("ELEVEN_API_KEY not set")

    voice_id = "pNInz6obpgDQGcFmaJgB"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    out = TMP / "eleven_voice.mp3"

    try:
        r = requests.post(
            url,
            json={"text": text},
            headers={
                "xi-api-key": api,
                "Content-Type": "application/json"
            }
        )

        if r.status_code != 200:
            raise RuntimeError(r.text)

        with open(out, "wb") as f:
            f.write(r.content)

        return out
    except Exception as e:
        raise RuntimeError(f"ElevenLabs failed: {e}")

# ============================================================
# Failover System
# ============================================================
def generate_voice_with_failover(text, preferred_gender="male"):
    providers = [
        ("elevenlabs", tts_elevenlabs),
        ("openai", tts_openai),
        ("gtts", tts_google),
    ]

    errors = []

    for name, provider in providers:
        try:
            print(f"[TTS] Trying {name}...")
            return provider(text, preferred_gender)
        except Exception as e:
            errors.append((name, str(e)))

    raise RuntimeError(f"All TTS failed: {errors}")
