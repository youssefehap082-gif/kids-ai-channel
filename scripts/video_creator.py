import os
import logging
import tempfile
from pathlib import Path

from pydub import AudioSegment
from gtts import gTTS
import requests

logger = logging.getLogger(__name__)

TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)


# ============================================================
# CLEAN TEXT FOR TTS
# ============================================================

def clean_text(text: str) -> str:
    if not text:
        return "This is an auto-generated narration."
    cleaned = (
        text.replace("*", " ")
            .replace("#", " ")
            .replace("•", " ")
            .replace("|", " ")
            .replace("–", "-")
            .strip()
    )
    return cleaned


# ============================================================
# 1) OPENAI TTS
# ============================================================

def tts_openai(text, gender="male"):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=key)

        voice = "alloy" if gender == "male" else "verse"

        logger.info("Trying OpenAI TTS...")

        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text
        )

        fp = TMP / "openai_voice.mp3"
        response.stream_to_file(fp)
        return fp
    except Exception as e:
        logger.error(f"OpenAI TTS failed: {e}")
        return None


# ============================================================
# 2) ELEVENLABS TTS
# ============================================================

def tts_eleven(text, gender="male"):
    key = os.getenv("ELEVEN_API_KEY")
    if not key:
        return None

    try:
        voice_id = "21m00Tcm4TlvDq8ikWAM" if gender == "male" else "EXAVITQu4vr4xnSDxMaL"

        logger.info("Trying ElevenLabs TTS...")

        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": key,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "voice_settings": {
                    "stability": 0.55,
                    "similarity_boost": 0.7
                }
            },
            timeout=30
        )

        if r.status_code != 200:
            raise RuntimeError(r.text)

        fp = TMP / "eleven_voice.mp3"
        with open(fp, "wb") as f:
            f.write(r.content)
        return fp
    except Exception as e:
        logger.error(f"ElevenLabs TTS failed: {e}")
        return None


# ============================================================
# 3) Google gTTS (Offline Fallback)
# ============================================================

def tts_gtts(text):
    try:
        logger.info("Trying gTTS fallback...")

        tts = gTTS(text=text, lang="en")
        fp = TMP / "gtts_voice.mp3"
        tts.save(fp)
        return fp
    except Exception as e:
        logger.error(f"gTTS failed: {e}")
        return None


# ============================================================
# 4) GEMINI AUDIO TTS
# ============================================================

def tts_gemini(text):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    try:
        logger.info("Trying Gemini TTS...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateSpeech?key={key}"

        req = {"text": text}
        r = requests.post(url, json=req, timeout=20)

        if r.status_code != 200:
            raise RuntimeError(r.text)

        audio_bytes = r.content

        fp = TMP / "gemini_voice.mp3"
        with open(fp, "wb") as f:
            f.write(audio_bytes)

        return fp
    except Exception as e:
        logger.error(f"Gemini TTS failed: {e}")
        return None


# ============================================================
# MASTER FAILOVER HANDLER
# ============================================================

def normalize_audio(path: Path):
    try:
        audio = AudioSegment.from_file(path)
        normalized = audio.normalize()
        normalized.export(path, format="mp3")
    except Exception:
        pass


def generate_voice_with_failover(text: str, preferred_gender="male"):
    text = clean_text(text)

    order = [
        ("openai", lambda: tts_openai(text, preferred_gender)),
        ("eleven", lambda: tts_eleven(text, preferred_gender)),
        ("gtts", lambda: tts_gtts(text)),
        ("gemini", lambda: tts_gemini(text)),
    ]

    errors = []

    for name, fn in order:
        try:
            out = fn()
            if out and out.exists() and out.stat().st_size > 500:
                normalize_audio(out)
                logger.info(f"TTS SUCCESS via: {name}")
                return out
        except Exception as e:
            errors.append((name, str(e)))

    raise RuntimeError(f"All TTS engines failed: {errors}")
