import os
from pathlib import Path
from gtts import gTTS
import requests

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / 'tmp'
VOICE_DIR = TMP / 'voices'
VOICE_DIR.mkdir(parents=True, exist_ok=True)

ELEVEN = os.getenv('ELEVEN_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI = os.getenv('GEMINI_API_KEY')

def gtts_tts(text, out_path=None):
    out_path = out_path or (VOICE_DIR / 'voice_gtts.mp3')
    t = gTTS(text=text, lang='en')
    t.save(str(out_path))
    return out_path

def eleven_tts(text, voice='alloy', out_path=None):
    if not ELEVEN:
        raise RuntimeError("ELEVEN_API_KEY missing")
    out_path = out_path or (VOICE_DIR / 'voice_eleven.mp3')
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {'xi-api-key': ELEVEN}
    payload = {"text": text}
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024*32):
            f.write(chunk)
    return out_path

def openai_tts(text, out_path=None):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI API key missing")
    # Note: OpenAI TTS endpoint usage may vary by SDK version - keep as illustrative
    import openai
    openai.api_key = OPENAI_API_KEY
    out_path = out_path or (VOICE_DIR / 'voice_openai.mp3')
    try:
        res = openai.audio.speech.create(model="gpt-4o-mini-tts", voice="alloy", input=text)
        with open(out_path, "wb") as f:
            f.write(res.read())
        return out_path
    except Exception as e:
        raise

def generate_voice_with_failover(text, preferred_gender='male'):
    errors = []
    # try Eleven
    try:
        v = 'alloy' if preferred_gender=='male' else 'sofia'
        return eleven_tts(text, voice=v)
    except Exception as e:
        errors.append(("eleven", str(e)))
    # try openai
    try:
        return openai_tts(text)
    except Exception as e:
        errors.append(("openai", str(e)))
    # final fallback gTTS
    try:
        return gtts_tts(text)
    except Exception as e:
        errors.append(("gtts", str(e)))
    raise RuntimeError(f"All TTS providers failed: {errors}")
