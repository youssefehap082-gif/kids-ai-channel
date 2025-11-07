# scripts/tts_gtts.py
import json, time, os
from gtts import gTTS
from pathlib import Path

OUT = Path("output")
script = json.load(open(OUT/"script.json", encoding="utf-8"))
scenes = script.get("scenes", [])

# create one narration combining captions with short pauses
texts = []
for s in scenes:
    texts.append(s.get("caption",""))
    texts.append(" ")  # short pause marker

full_text = " .  ".join(texts).strip()
if not full_text:
    print("No captions found")
else:
    tts = gTTS(full_text, lang='en', slow=False)
    outp = OUT / "narration.mp3"
    tts.save(str(outp))
    print("Saved narration", outp)
