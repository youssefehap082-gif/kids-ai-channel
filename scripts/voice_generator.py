import os
import logging
import time
from pathlib import Path
from pydub import AudioSegment
import requests

logger = logging.getLogger("voice_generator")
logger.setLevel(logging.INFO)

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVEN_KEY = os.getenv("ELEVEN_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

TMP = Path("data/tmp_audio")
TMP.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def _save_temp(buf: bytes, suffix=".mp3"):
    """Save temporary audio file."""
    fname = TMP / f"voice_{int(time.time()*1000)}{suffix}"
    with open(fname, "wb") as f:
        f.write(buf)
    return fname


def _normalize_audio(path: Path, target_dbfs=-14):
    """Normalize audio to consistent loudness."""
    audio = AudioSegment.from_file(path)
    change = target_dbfs - audio.dBFS
    normalized = audio.apply_gain(change)
    normalized.export(path, format="mp3")
    return path


def _retry(fn, tries=3, wait=1):
    last = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            last = e
            logger.warning(f"TTS retry {i+1}/{tries} failed: {e}")
            time.sleep(wait)
    raise last


# -------------------------------------------------------
# Provider 1) OPENAI TTS  (أفضل جودة)
# -------------------------------------------------------
def _tts_openai(text: str, voice: str = "alloy"):
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY missing")

    import openai
    openai.api_key = OPENAI_KEY

    try:
        client = openai.OpenAI(api_key=OPENAI_KEY)
        resp = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text
        )
        audio_bytes = resp.read()
        return _save_temp(audio_bytes, ".mp3")
    except Exception as e:
        raise RuntimeError(f"OpenAI TTS failed: {e}")


# -------------------------------------------------------
# Provider 2) ElevenLabs (الأفضل بعد OpenAI)
# -------------------------------------------------------
def _tts_eleven(text: str, voice_gender="male"):
    if not ELEVEN_KEY:
        raise RuntimeError("ELEVEN_API_KEY missing")

    voice_id = "pNInz6obpgDQGcFmaJgB" if voice_gender == "male" else "EXAVITQu4vr4xnSDxMaL"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.7}
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=40)
        r.raise_for_status()
        return _save_temp(r.content, ".mp3")
    except Exception as e:
        raise RuntimeError(f"ElevenLabs TTS failed: {e}")


# -------------------------------------------------------
# Provider 3) gTTS (أبطأ – لكن ثابت)
# -------------------------------------------------------
def _tts_gtts(text: str):
    try:
        from gtts import gTTS
        tts = gTTS(text, lang="en")
        buf = TMP / f"gtts_{int(time.time()*1000)}.mp3"
        tts.save(str(buf))
        return buf
    except Exception as e:
        raise RuntimeError(f"gTTS failed: {e}")


# -------------------------------------------------------
# Provider 4) Gemini Audio
# -------------------------------------------------------
def _tts_gemini(text: str):
    if not GEMINI_KEY:
        raise RuntimeError("GEMINI_API_KEY missing")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"

    payload = {
        "contents": [{
            "parts": [
                {"text": text}
            ]
        }]
    }

    try:
        r = requests.post(url, json=payload, timeout=40)
        r.raise_for_status()

        data = r.json()

        audio_base64 = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("audioData")
        )

        if not audio_base64:
            raise RuntimeError("Gemini returned no audio")

        import base64
        audio_bytes = base64.b64decode(audio_base64)

        return _save_temp(audio_bytes)
    except Exception as e:
        raise RuntimeError(f"Gemini TTS failed: {e}")


# -------------------------------------------------------
# Unified function — auto fallback TTS
# -------------------------------------------------------
def generate_voice_with_failover(
    text: str,
    preferred_gender: str = "male"
) -> Path:
    """
    Attempts TTS in this order:
    1) OpenAI TTS
    2) ElevenLabs
    3) Gemini Audio
    4) gTTS
    """

    providers = [
        ("openai", lambda: _tts_openai(text)),
        ("eleven", lambda: _tts_eleven(text, preferred_gender)),
        ("gemini", lambda: _tts_gemini(text)),
        ("gtts", lambda: _tts_gtts(text))
    ]

    errors = []

    for name, fn in providers:
        try:
            logger.info(f"Trying TTS provider: {name}")
            out = _retry(fn, tries=2, wait=1)
            out = _normalize_audio(out)
            logger.info(f"TTS provider worked: {name}")
            return out
        except Exception as e:
            errors.append((name, str(e)))
            logger.warning(f"TTS provider failed: {name} → {e}")

    logger.error(f"All TTS providers failed: {errors}")
    raise RuntimeError(f"All TTS failed: {errors}")
