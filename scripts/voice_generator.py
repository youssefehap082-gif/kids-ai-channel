# voice_generator.py
# Multi-tier TTS: ElevenLabs -> OpenAI TTS -> OpenTTS (self-hosted API via OPENTTS_URL) -> gTTS fallback
# Returns path to an MP3 file.

import os
import requests
from pathlib import Path
from typing import Optional
import time

OUT = Path(__file__).resolve().parent / 'tmp'
OUT.mkdir(exist_ok=True)

ELEVEN = os.getenv('ELEVENAPIKEY')        # ElevenLabs API key
OPENAI_KEY = os.getenv('OPENAIAPIKEY')    # OpenAI API key (used for TTS fallback)
OPENTTS_URL = os.getenv('OPENTTS_URL')    # Optional: URL for an OpenTTS-like server (e.g., http://localhost:5002/api/tts)

def eleven_tts(text, voice='alloy', out_path: Optional[Path]=None, timeout=60):
    if not ELEVEN:
        raise RuntimeError('ELEVENAPIKEY missing')
    if out_path is None:
        out_path = OUT / f'voice_eleven_{int(time.time())}.mp3'
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice}'
    headers = {'xi-api-key': ELEVEN, 'Content-Type': 'application/json'}
    payload = {'text': text, 'voice_settings': {'stability': 0.6, 'similarity_boost': 0.75}}
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=timeout)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024 * 32):
            f.write(chunk)
    return out_path

def openai_tts(text, voice='alloy', out_path: Optional[Path]=None, timeout=60):
    if not OPENAI_KEY:
        raise RuntimeError('OPENAIAPIKEY missing')
    if out_path is None:
        out_path = OUT / f'voice_openai_{int(time.time())}.mp3'
    url = 'https://api.openai.com/v1/audio/speech'
    headers = {'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'}
    payload = {
        'model': 'gpt-4o-mini-tts',
        'voice': voice,
        'input': text
    }
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=timeout)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024 * 32):
            f.write(chunk)
    return out_path

def opentts_tts(text, voice='en', out_path: Optional[Path]=None, timeout=60):
    if not OPENTTS_URL:
        raise RuntimeError('OPENTTS_URL not configured')
    if out_path is None:
        out_path = OUT / f'voice_opentts_{int(time.time())}.mp3'
    url = OPENTTS_URL
    try:
        r = requests.post(url, json={'text': text, 'voice': voice}, stream=True, timeout=timeout)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(1024 * 32):
                f.write(chunk)
        return out_path
    except Exception:
        r = requests.post(f"{url}?voice={voice}", data=text.encode('utf-8'), stream=True, timeout=timeout)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(1024 * 32):
                f.write(chunk)
        return out_path

def gtts_tts(text, lang='en', out_path: Optional[Path]=None):
    try:
        from gtts import gTTS
    except Exception as e:
        raise RuntimeError('gTTS not installed') from e
    if out_path is None:
        out_path = OUT / f'voice_gtts_{int(time.time())}.mp3'
    t = gTTS(text, lang=lang)
    t.save(str(out_path))
    return out_path

def generate_voice_with_failover(text, preferred_gender='male'):
    errors = []
    eleven_voice = 'alloy' if preferred_gender == 'male' else 'sofia'
    openai_voice = 'alloy' if preferred_gender == 'male' else 'sofia'
    opentts_voice = 'alloy' if preferred_gender == 'male' else 'sofia'
    try:
        return eleven_tts(text, voice=eleven_voice)
    except Exception as e:
        errors.append(('eleven', str(e)))
    try:
        return openai_tts(text, voice=openai_voice)
    except Exception as e:
        errors.append(('openai', str(e)))
    try:
        return opentts_tts(text, voice=opentts_voice)
    except Exception as e:
        errors.append(('opentts', str(e)))
    try:
        return gtts_tts(text, lang='en')
    except Exception as e:
        errors.append(('gtts', str(e)))
    raise RuntimeError(f'All TTS providers failed: {errors}')
