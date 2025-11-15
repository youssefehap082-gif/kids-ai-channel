from gtts import gTTS
import uuid

def generate_voice_with_failover(text, gender="male"):
    out = f"/tmp/voice_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text, lang="en", tld="com", slow=False)
    tts.save(out)
    return out
