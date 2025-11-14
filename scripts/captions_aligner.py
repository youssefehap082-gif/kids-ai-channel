# captions_aligner.py
# High-level helper to generate accurate SRT using forced-alignment (aeneas) when possible,
# otherwise falls back to naive distribution.

from pathlib import Path
from .captions_uploader import create_srt_from_script, align_with_aeneas

def generate_best_srt(script_text, audio_path, out_srt_path: Path, duration, lang='eng'):
    # try aeneas forced alignment first
    srt = None
    try:
        srt = align_with_aeneas(script_text, audio_path, out_srt_path, lang=lang)
    except Exception as e:
        print('Aeneas not available or failed:', e)
        srt = None
    if srt and out_srt_path.exists():
        return out_srt_path
    # fallback: naive SRT
    return create_srt_from_script(script_text, duration, out_srt_path)
