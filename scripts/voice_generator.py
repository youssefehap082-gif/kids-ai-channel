import os, time, requests
from pathlib import Path
OUT = Path(__file__).resolve().parent / 'tmp'
OUT.mkdir(exist_ok=True)
ELEVEN = os.getenv('ELEVEN_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
def eleven_tts(text, voice='alloy', out_path=None):
    if not ELEVEN:
        raise RuntimeError('ELEVEN_API_KEY missing')
    if out_path is None:
        out_path = OUT / f'voice_eleven_{int(time.time())}.mp3'
    url = 'https://api.elevenlabs.io/v1/text-to-speech/' + voice
    headers = {'xi-api-key': ELEVEN, 'Content-Type': 'application/json'}
    payload = {'text': text, 'voice_settings': {'stability': 0.6, 'similarity_boost': 0.75}}
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024*32):
            f.write(chunk)
    return out_path
def openai_tts(text, out_path=None):
    if not OPENAI_KEY:
        raise RuntimeError('OPENAI_KEY missing')
    if out_path is None:
        out_path = OUT / f'voice_openai_{int(time.time())}.mp3'
    url = 'https://api.openai.com/v1/audio/speech'
    headers = {'Authorization': f'Bearer {OPENAI_KEY}', 'Content-Type': 'application/json'}
    payload = {'model':'gpt-4o-mini-tts','voice':'alloy','input':text}
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        for chunk in r.iter_content(1024*32):
            f.write(chunk)
    return out_path
def generate_voice_with_failover(text, preferred_gender='male'):
    voices = {'male':'alloy','female':'sofia'}
    errors = []
    try:
        return eleven_tts(text, voice=voices.get(preferred_gender,'alloy'))
    except Exception as e:
        errors.append(('eleven',str(e)))
    try:
        return openai_tts(text)
    except Exception as e:
        errors.append(('openai',str(e)))
    raise RuntimeError(f'All TTS failed: {errors}')
