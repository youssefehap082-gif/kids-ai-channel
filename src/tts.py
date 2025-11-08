import os, requests, time
from pathlib import Path
from gtts import gTTS  # backup
import json

# مفاتيح الـ APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "")  # ضيفه في secrets
OPENAI_TTS_MODEL = "gpt-4o-mini-tts"
VOICES_ROTATION = os.getenv("VOICES_ROTATION", "alloy,verse").split(",")

# =======================
#   OPENAI TTS
# =======================
def openai_tts(text: str, out_path: Path, idx: int = 0) -> bool:
    voice = VOICES_ROTATION[idx % len(VOICES_ROTATION)].strip() or "alloy"
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": OPENAI_TTS_MODEL, "voice": voice, "input": text}
    for attempt in range(6):
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            out_path.write_bytes(r.content)
            time.sleep(5)
            return True
        elif r.status_code == 429:
            wait = 10 + attempt * 5
            print(f"⚠️ OpenAI rate limit (attempt {attempt+1}) → waiting {wait}s...")
            time.sleep(wait)
        else:
            print(f"⚠️ OpenAI TTS error {r.status_code}: {r.text[:100]}")
            return False
    print("⚠️ OpenAI TTS failed after all retries.")
    return False

# =======================
#   ELEVENLABS TTS
# =======================
def eleven_tts(text: str, out_path: Path) -> bool:
    if not ELEVEN_API_KEY:
        return False
    try:
        print("🎙️ Using ElevenLabs voice...")
        voice_id = "EXAVITQu4vr4xnSDxMaL"  # voice: Adam
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json",
            "accept": "audio/mpeg"
        }
        data = {"text": text, "voice_settings": {"stability": 0.4, "similarity_boost": 0.9}}
        r = requests.post(url, headers=headers, json=data)
        if r.status_code == 200:
            out_path.write_bytes(r.content)
            time.sleep(3)
            return True
        else:
            print(f"⚠️ ElevenLabs failed: {r.status_code} {r.text[:120]}")
            return False
    except Exception as e:
        print(f"⚠️ ElevenLabs exception: {e}")
        return False

# =======================
#   GTTS (fallback)
# =======================
def gtts_fallback(text: str, out_path: Path):
    try:
        print("🔄 Using Google gTTS fallback...")
        gTTS(text=text, lang="en", slow=False).save(str(out_path))
        time.sleep(2)
    except Exception as e:
        print(f"❌ gTTS failed: {e}")
        raise e

# =======================
#   SYNTHESIZE WRAPPER
# =======================
def synthesize(text: str, out_path: Path, idx: int = 0) -> Path:
    """توليد صوت ذكي باختيار المصدر الأفضل المتاح."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 1️⃣ جرب OpenAI أولًا
    if OPENAI_API_KEY and openai_tts(text, out_path, idx):
        return out_path

    # 2️⃣ جرب ElevenLabs لو متاح
    if ELEVEN_API_KEY and eleven_tts(text, out_path):
        return out_path

    # 3️⃣ fallback إلى gTTS
    gtts_fallback(text, out_path)
    return out_path
