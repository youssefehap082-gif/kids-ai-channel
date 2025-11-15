import os, requests
from pathlib import Path
from gtts import gTTS

OUT = Path(__file__).resolve().parent / "tmp"
OUT.mkdir(exist_ok=True)

def eleven_tts(text, voice="alloy", out_path=None):
    key = os.getenv("ELEVEN_API_KEY")
    if not key:
        raise RuntimeError("ELEVEN_API_KEY missing")
    if out_path is None:
        out_path = OUT / "voice_eleven.mp3"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {"xi-api-key": key, "Content-Type": "application/json"}
    payload = {"text": text, "voice_settings": {"stability":0.6,"similarity_boost":0.75}}
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for ch in r.iter_content(1024*32):
            f.write(ch)
    return str(out_path)

def openai_tts(text, out_path=None):
    import openai
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing")
    openai.api_key = key
    if out_path is None:
        out_path = OUT / "voice_openai.mp3"
    # use speech synthesis endpoint if available
    resp = openai.audio.speech.create(model="gpt-4o-mini-tts", voice="alloy", input=text)
    with open(out_path, "wb") as f:
        f.write(resp)
    return str(out_path)

def gtts_fallback(text, out_path=None):
    if out_path is None:
        out_path = OUT / "voice_gtts.mp3"
    tts = gTTS(text)
    tts.save(str(out_path))
    return str(out_path)

def generate_voice_with_failover(text, preferred_gender="male"):
    errors = []
    # try Eleven
    try:
        return eleven_tts(text, voice="alloy")
    except Exception as e:
        errors.append(("eleven", str(e)))
    # try OpenAI TTS
    try:
        return openai_tts(text)
    except Exception as e:
        errors.append(("openai", str(e)))
    # fallback gTTS
    try:
        return gtts_fallback(text)
    except Exception as e:
        errors.append(("gtts", str(e)))
    raise RuntimeError("All TTS failed: " + str(errors))
