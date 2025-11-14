import os
import time
import requests
from pathlib import Path
from gtts import gTTS

OUT = Path(__file__).resolve().parent / 'tmp'
OUT.mkdir(exist_ok=True)

ELEVEN = os.getenv('ELEVEN_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

# ---------------------------------------------------
# 1) ElevenLabs TTS (اول محاولة)
# ---------------------------------------------------
def eleven_tts(text, voice='alloy', out_path=None):
    if not ELEVEN:
        raise RuntimeError('ELEVEN_API_KEY missing')

    if out_path is None:
        out_path = OUT / f'voice_eleven_{int(time.time())}.mp3'

    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice}'
    headers = {'xi-api-key': ELEVEN, 'Content-Type': 'application/json'}
    payload = {'text': text, 'voice_settings': {'stability': 0.6, 'similarity_boost': 0.75}}

    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    r.raise_for_status()

    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024 * 32):
            f.write(chunk)

    return out_path

# ---------------------------------------------------
# 2) OpenAI TTS (ثاني محاولة)
# ---------------------------------------------------
def openai_tts(text, out_path=None):
    if not OPENAI_KEY:
        raise RuntimeError('OPENAI_KEY missing')

    if out_path is None:
        out_path = OUT / f'voice_openai_{int(time.time())}.mp3'

    url = "https://api.openai.com/v1/audio/speech"
    headers = {'Authorization': f'Bearer {OPENAI_KEY}',
               'Content-Type': 'application/json'}

    payload = {
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",
        "input": text
    }

    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    r.raise_for_status()

    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024 * 32):
            f.write(chunk)

    return out_path

# ---------------------------------------------------
# 3) gTTS fallback (مستحيل تفشل)
# ---------------------------------------------------
def gtts_fallback(text, out_path=None):
    if out_path is None:
        out_path = OUT / f"voice_gtts_{int(time.time())}.mp3"

    tts = gTTS(text=text, lang='en')
    tts.save(out_path)

    return out_path

# ---------------------------------------------------
# MASTER FAILOVER LOGIC — ALWAYS RETURNS AUDIO
# ---------------------------------------------------
def generate_voice_with_failover(text, preferred_gender='male'):

    voices = {
        'male': 'alloy',
        'female': 'sofia'
    }

    errors = []

    # 1) Try ElevenLabs
    try:
        return eleven_tts(text, voice=voices.get(preferred_gender, 'alloy'))
    except Exception as e:
        errors.append(("ElevenLabs", str(e)))

    # 2) Try OpenAI
    try:
        return openai_tts(text)
    except Exception as e:
        errors.append(("OpenAI", str(e)))

    # 3) Final fallback: Google gTTS
    try:
        return gtts_fallback(text)
    except Exception as e:
        errors.append(("gTTS", str(e)))

    # If even GTTS exploded (مستحيل)
    raise RuntimeError(f"EXTREME ERROR — ALL TTS failed: {errors}")
