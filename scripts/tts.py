"""
scripts/tts.py
Wrapper to call TTS providers in priority order.
Uses env vars: ELEVEN_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY
Returns local path to audio file (wav) for given text.
"""
import os
import logging
from typing import List
from pathlib import Path
from scripts.utils.http import post, get

logger = logging.getLogger("kids_ai.tts")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

OUTPUT_DIR = os.getenv("TTS_OUTPUT_DIR", "/tmp/tts")
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def eleven_tts(text: str, voice: str="alloy") -> str:
    key = os.getenv("ELEVEN_API_KEY")
    if not key:
        raise RuntimeError("ELEVEN_API_KEY not set")
    # Placeholder: implement elevenlabs SDK call here
    out = os.path.join(OUTPUT_DIR, f"eleven_{abs(hash(text))%100000}.wav")
    with open(out, "wb") as f:
        f.write(b"")  # placeholder empty file; replace with actual audio bytes
    logger.info("ElevenLabs placeholder produced %s", out)
    return out

def gtts_fallback(text: str) -> str:
    out = os.path.join(OUTPUT_DIR, f"gtts_{abs(hash(text))%100000}.wav")
    with open(out, "wb") as f:
        f.write(b"")
    return out

def generate_tts_for_facts(facts: List[str], voices: List[str]) -> List[str]:
    audios = []
    for i, fact in enumerate(facts):
        voice = voices[i % len(voices)] if voices else voices[0]
        try:
            path = eleven_tts(fact, voice=voice)
        except Exception as e:
            logger.warning("Eleven failed, trying gTTS: %s", e)
            path = gtts_fallback(fact)
        audios.append(path)
    return audios
