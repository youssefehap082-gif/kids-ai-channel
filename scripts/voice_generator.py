# scripts/voice_generator.py (مقتطف - دالة failover)
import os
from pathlib import Path
import requests
import logging
LOG = logging.getLogger(__name__)

ELEVEN_KEY = os.getenv('ELEVEN_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def generate_voice_with_failover(text, preferred_gender='male'):
    errors = []
    # 1) ElevenLabs
    if ELEVEN_KEY:
        try:
            # simplified ElevenLabs call
            out = TMP / 'voice_eleven.mp3'
            # ... implement ElevenLabs API call here ...
            # if success: return out
        except Exception as e:
            errors.append(('eleven', str(e)))

    # 2) OpenAI TTS
    if OPENAI_KEY:
        try:
            out = TMP / 'voice_openai.mp3'
            # ... implement openai audio.speech with openai package ...
            # if success: return out
        except Exception as e:
            errors.append(('openai', str(e)))

    # 3) gTTS fallback
    try:
        from gtts import gTTS
        out = TMP / 'voice_gtts.mp3'
        tts = gTTS(text, lang='en')
        tts.save(str(out))
        return out
    except Exception as e:
        errors.append(('gtts', str(e)))

    raise RuntimeError(f'All TTS failed: {errors}')
