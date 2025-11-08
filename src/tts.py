import os, requests, random, time
from pathlib import Path
from gtts import gTTS  # مكتبة Google Text-to-Speech

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
VOICES_ROTATION = os.getenv("VOICES_ROTATION", "alloy,verse").split(",")

def synthesize_with_openai(text: str, out_path: Path, idx: int = 0) -> bool:
    """حاول توليد الصوت باستخدام OpenAI TTS."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    voice = VOICES_ROTATION[idx % len(VOICES_ROTATION)].strip() or "alloy"
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": OPENAI_TTS_MODEL, "voice": voice, "input": text}

    for attempt in range(8):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=600)
            if r.status_code == 200:
                out_path.write_bytes(r.content)
                time.sleep(8)  # راحة قصيرة لتفادي الضغط
                return True
            elif r.status_code == 429:
                wait = 10 + attempt * 5
                print(f"⚠️ OpenAI rate limit (attempt {attempt+1}) → waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                print(f"❌ Unexpected status {r.status_code}: {r.text[:100]}")
                return False
        except Exception as e:
            print(f"⚠️ OpenAI TTS failed attempt {attempt+1}: {e}")
            time.sleep(5)
    print("⚠️ OpenAI TTS failed after all retries.")
    return False

def synthesize_with_gtts(text: str, out_path: Path):
    """توليد الصوت باستخدام Google TTS كبديل."""
    try:
        print("🔄 Switching to Google TTS fallback...")
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(str(out_path))
        time.sleep(3)
    except Exception as e:
        print(f"❌ gTTS failed: {e}")
        raise e

def synthesize(text: str, out_path: Path, idx: int = 0) -> Path:
    """
    يحاول أولاً عبر OpenAI TTS.
    لو فشل أو اتأخر أو واجه 429، يستخدم gTTS تلقائيًا.
    """
    success = synthesize_with_openai(text, out_path, idx=idx)
    if not success:
        synthesize_with_gtts(text, out_path)
    return out_path
