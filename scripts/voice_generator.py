#!/usr/bin/env python3
"""
Voice generator with failover sequence:
1) ElevenLabs (if ELEVEN_API_KEY present)
2) OpenAI TTS (if OPENAI_API_KEY present)
3) gTTS fallback (always)
Returns path to mp3 file.
"""
import os, logging, time
from pathlib import Path
import requests

log = logging.getLogger('voice_gen')
TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

ELEVEN_KEY = os.getenv('ELEVEN_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def eleven_tts(text, voice='alloy', out_path=None):
    if not ELEVEN_KEY:
        raise RuntimeError('ELEVEN_API_KEY not set')
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice}'
    headers = {'Accept': 'audio/mpeg', 'xi-api-key': ELEVEN_KEY, 'Content-Type': 'application/json'}
    payload = {"text": text}
    out_path = out_path or (TMP / 'voice_eleven.mp3')
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024*32):
            f.write(chunk)
    return str(out_path)

def openai_tts(text, model="gpt-4o-mini-tts", out_path=None):
    """
    Uses the openai Python client if available. We implement a minimal HTTP call fallback in case
    the official client isn't accessible in runner. This function expects OPENAI_KEY env var.
    """
    if not OPENAI_KEY:
        raise RuntimeError('OPENAI_API_KEY not set')
    out_path = out_path or (TMP / 'voice_openai.mp3')
    try:
        # try official client
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        # modern usage: client.audio.speech.create(...)
        # Some environments will not have the method; wrap in try/except
        try:
            resp = client.audio.speech.create(model=model, voice="alloy", input=text)
            # resp is bytes-like in some clients; attempt write
            if isinstance(resp, (bytes, bytearray)):
                with open(out_path, 'wb') as f:
                    f.write(resp)
                return str(out_path)
            # if resp has .read()
            try:
                content = resp.read()
                with open(out_path, 'wb') as f:
                    f.write(content)
                return str(out_path)
            except Exception:
                pass
        except Exception:
            pass
    except Exception:
        pass

    # fallback: attempt httpx/post to openai audio endpoint
    try:
        import httpx
        headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
        data = {"model": model, "input": text}
        r = httpx.post("https://api.openai.com/v1/audio/speech", json=data, headers=headers, timeout=60)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            f.write(r.content)
        return str(out_path)
    except Exception as e:
        raise RuntimeError(f"OpenAI TTS failed: {e}")

def gtts_fallback(text, out_path=None):
    try:
        from gtts import gTTS
    except Exception as e:
        raise RuntimeError(f"gTTS import failed: {e}")
    out_path = out_path or (TMP / 'voice_gtts.mp3')
    t = gTTS(text=text, lang='en')
    t.save(str(out_path))
    return str(out_path)

def generate_voice_with_failover(text, preferred_gender='male'):
    errors = []
    # Attempt ElevenLabs
    if ELEVEN_KEY:
        try:
            return eleven_tts(text, voice='alloy')
        except Exception as e:
            log.warning("ElevenLabs TTS failed: %s", e)
            errors.append(('eleven', str(e)))
            time.sleep(0.5)
    # Attempt OpenAI TTS
    if OPENAI_KEY:
        try:
            return openai_tts(text)
        except Exception as e:
            log.warning("OpenAI TTS failed: %s", e)
            errors.append(('openai', str(e)))
            time.sleep(0.5)
    # Fallback to gTTS
    try:
        return gtts_fallback(text)
    except Exception as e:
        errors.append(('gtts', str(e)))
    raise RuntimeError(f"All TTS failed: {errors}")
