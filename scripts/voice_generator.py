import os, requests
from pathlib import Path
from gtts import gTTS
TMP = Path(__file__).resolve().parent / 'tmp_voice'
TMP.mkdir(parents=True, exist_ok=True)
ELEVEN = os.getenv('ELEVEN_API_KEY')
OPENAI = os.getenv('OPENAI_API_KEY')
def tts_eleven(text, voice='alloy', out=None):
    if not ELEVEN: raise RuntimeError('ELEVEN missing')
    if out is None: out = TMP / 'eleven.mp3'
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice}'
    r = requests.post(url, json={'text':text}, headers={'xi-api-key':ELEVEN}, stream=True, timeout=30)
    r.raise_for_status()
    with open(out,'wb') as f:
        for chunk in r.iter_content(1024*32): f.write(chunk)
    return out
def tts_openai(text, out=None):
    if not OPENAI: raise RuntimeError('OPENAI missing')
    if out is None: out = TMP / 'openai.mp3'
    url = 'https://api.openai.com/v1/audio/speech'
    r = requests.post(url, json={'model':'gpt-4o-mini-tts','input':text}, headers={'Authorization':f'Bearer {OPENAI}'}, timeout=30)
    r.raise_for_status()
    with open(out,'wb') as f: f.write(r.content)
    return out
def tts_gtts(text, out=None):
    if out is None: out = TMP / 'gtts.mp3'
    gTTS(text=text, lang='en').save(out)
    return out
def generate_voice_with_failover(text):
    errs = []
    for fn in (tts_eleven, tts_openai, tts_gtts):
        try:
            return fn(text)
        except Exception as e:
            errs.append(str(e))
    raise RuntimeError('All TTS failed: '+str(errs))
