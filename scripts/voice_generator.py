import os
import logging
import time
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment
import requests

logger = logging.getLogger("voice_generator")

TMP = Path(__file__).resolve().parent / "tmp_voice"
TMP.mkdir(exist_ok=True)


# --------------------------------------------------
# Helper: save raw bytes to file
# --------------------------------------------------
def save_audio_bytes(data, path):
    with open(path, "wb") as f:
        f.write(data)
    return path


# --------------------------------------------------
# PROVIDER 1 — OpenAI TTS
# --------------------------------------------------
def tts_openai(text, gender="male"):
    try:
        import openai

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        voice = "alloy" if gender == "male" else "verse"

        logger.info("Using OpenAI TTS...")
        result = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text
        )

        audio_bytes = result.read()

        out_path = TMP / "openai_tts.mp3"
        return save_audio_bytes(audio_bytes, out_path)

    except Exception as e:
        raise RuntimeError(f"OpenAI TTS failed: {e}")


# --------------------------------------------------
# PROVIDER 2 — ElevenLabs
# --------------------------------------------------
def tts_elevenlabs(text, gender="male"):
    try:
        API_KEY = os.getenv("ELEVEN_API_KEY")
        if not API_KEY:
            raise RuntimeError("Missing ELEVEN_API_KEY")

        voice_id = "pNInz6obpgDQGcFmaJgB" if gender == "male" else "TxGEqnHWrfWFTfGW9XjX"

        logger.info("Using ElevenLabs TTS...")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.65}
        }

        res = requests.post(url, json=payload, headers=headers)
        if res.status_code != 200:
            raise RuntimeError(res.text)

        out_path = TMP / "eleven_tts.mp3"
        return save_audio_bytes(res.content, out_path)

    except Exception as e:
        raise RuntimeError(f"ElevenLabs TTS failed: {e}")


# --------------------------------------------------
# PROVIDER 3 — Google gTTS (always available)
# --------------------------------------------------
def tts_gtts(text, gender="male"):
    try:
        logger.info("Using Google gTTS...")
        tts = gTTS(text=text, lang="en")
        out_path = TMP / "gtts_tts.mp3"
        tts.save(out_path)
        return out_path
    except Exception as e:
        raise RuntimeError(f"gTTS failed: {e}")


# --------------------------------------------------
# PROVIDER 4 — Gemini Audio (fallback)
# --------------------------------------------------
def tts_gemini(text, gender="male"):
    try:
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        logger.info("Using Gemini Audio...")

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(
            [
                {"text": text},
            ],
            generation_config={"audio": {"voice": gender}}
        )

        audio = response._result.audio.data  # raw bytes

        out_path = TMP / "gemini_tts.mp3"
        return save_audio_bytes(audio, out_path)

    except Exception as e:
        raise RuntimeError(f"Gemini TTS failed: {e}")


# --------------------------------------------------
# Fallback system (OpenAI → Eleven → gTTS → Gemini)
# --------------------------------------------------
def generate_voice_with_failover(text, gender="male"):
    providers = [
        ("openai", tts_openai),
        ("elevenlabs", tts_elevenlabs),
        ("gtts", tts_gtts),
        ("gemini", tts_gemini),
    ]

    errors = []

    for name, func in providers:
        for attempt in range(3):  # auto retry
            try:
                logger.info(f"TTS Provider: {name} (attempt {attempt+1})")
                path = func(text, gender)
                logger.info(f"TTS success from {name}")
                return path

            except Exception as e:
                logger.error(f"{name} failed: {e}")
                errors.append(f"{name}: {e}")
                time.sleep(1.2)

    raise RuntimeError(f"All TTS providers failed: {errors}")
