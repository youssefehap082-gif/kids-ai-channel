#!/usr/bin/env python3
import os
from pathlib import Path
OUT = Path(__file__).resolve().parent / 'tmp'
OUT.mkdir(exist_ok=True)

def eleven_tts(text, voice='alloy', out_path=None):
    key = os.getenv('ELEVEN_API_KEY')
    if not key:
        raise RuntimeError('ELEVENAPIKEY missing')
    import requests
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice}'
    headers = {'xi-api-key': key, 'Content-Type': 'application/json'}
    payload = {"text": text}
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
    r.raise_for_status()
    out_path = out_path or OUT / 'voice_eleven.mp3'
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024*32):
            f.write(chunk)
    return str(out_path)

def gtts_fallback(text, out_path=None):
    from gtts import gTTS
    out_path = out_path or OUT / 'voice_gtts.mp3'
    t = gTTS(text=text, lang='en')
    t.save(str(out_path))
    return str(out_path)

def openai_tts(text, out_path=None):
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise RuntimeError('OPENAI missing')
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        # Attempt a modern audio endpoint; if not available this will raise
        res = client.audio.speech.create(model="gpt-4o-mini-tts", voice="alloy", input=text)
        out_path = out_path or OUT / 'voice_openai.mp3'
        with open(out_path, 'wb') as f:
            f.write(res)
        return str(out_path)
    except Exception:
        raise

def generate_voice(text):
    errs = []
    try:
        return eleven_tts(text)
    except Exception as e:
        errs.append(("eleven", str(e)))
    try:
        return openai_tts(text)
    except Exception as e:
        errs.append(("openai", str(e)))
    try:
        return gtts_fallback(text)
    except Exception as e:
        errs.append(("gtts", str(e)))
    raise RuntimeError(f"All TTS failed: {errs}")
