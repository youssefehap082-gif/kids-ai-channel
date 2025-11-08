import os, requests, random, time
from pathlib import Path
from tenacity import retry, wait_exponential, stop_after_attempt

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL","gpt-4o-mini-tts")

VOICES_ROTATION = os.getenv("VOICES_ROTATION","alloy,verse").split(",")

@retry(wait=wait_exponential(multiplier=2, min=2, max=20), stop=stop_after_attempt(5))
def synthesize(text: str, out_path: Path, idx: int = 0) -> Path:
    """Generate TTS with retry and rate-limit handling."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    voice = VOICES_ROTATION[idx % len(VOICES_ROTATION)].strip() or "alloy"
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": OPENAI_TTS_MODEL, "voice": voice, "input": text}
    r = requests.post(url, headers=headers, json=payload, timeout=600)
    if r.status_code == 429:
        print("⚠️ Rate limit hit, waiting 5 s then retrying…")
        time.sleep(5)
        raise Exception("retry")
    r.raise_for_status()
    out_path.write_bytes(r.content)
    time.sleep(3)  # cool-down between TTS calls
    return out_path
