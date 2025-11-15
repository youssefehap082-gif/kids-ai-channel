from gtts import gTTS
import uuid, os
def generate_voice_with_failover(text, preferred_gender='male'):
    out = f"/tmp/voice_{uuid.uuid4().hex}.mp3"
    try:
        tts = gTTS(text, lang='en', tld='com', slow=False)
        tts.save(out)
        return out
    except Exception:
        fallback = '/tmp/voice_fallback.mp3'
        open(fallback, 'wb').close()
        return fallback
