import os, requests, random
from pathlib import Path

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL","gpt-4o-mini-tts")

# بنبدّل بين صوتين (لو واحد مش متاح، هنرجع للأول)
VOICES_ROTATION = os.getenv("VOICES_ROTATION","alloy,verse").split(",")

def synthesize(text: str, out_path: Path, idx: int = 0) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    voice = VOICES_ROTATION[idx % max(1, len(VOICES_ROTATION))].strip() or "alloy"
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type":"application/json"}
    payload = {"model": OPENAI_TTS_MODEL, "voice": voice, "input": text}
    r = requests.post(url, headers=headers, json=payload, timeout=600)
    if r.status_code >= 400 and len(VOICES_ROTATION) > 1:
        # جرّب الصوت الأول كبديل
        payload["voice"] = VOICES_ROTATION[0].strip()
        r = requests.post(url, headers=headers, json=payload, timeout=600)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    return out_path
