# tools/tts_free.py
from gtts import gTTS
import os

def synthesize_free_tts(text, out_path="output.mp3", lang="en", slow=False):
    # gTTS saves mp3 file
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(out_path)
    return out_path
