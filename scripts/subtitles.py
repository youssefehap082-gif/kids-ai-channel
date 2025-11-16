# scripts/subtitles.py
"""
Generate very simple SRT subtitles from script text.
This is a pragmatic approach: split script lines into timed captions.
For production you'd use forced-alignment; this is a functional fallback.
"""
from pathlib import Path
import re
from typing import List
from datetime import timedelta
import logging

log = logging.getLogger("subtitles")
TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)


def _format_time(t_seconds: float) -> str:
    td = timedelta(seconds=round(t_seconds))
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},000"


def generate_subtitles(script_text: str, avg_words_per_min=150) -> str:
    """
    Splits script into lines and assigns rough timings.
    Returns path to .srt file.
    """
    lines = [l.strip() for l in re.split(r'[\n\r]+', script_text) if l.strip()]
    if not lines:
        return ""

    # estimate total words
    total_words = sum(len(l.split()) for l in lines)
    minutes = total_words / avg_words_per_min
    total_seconds = max(10, int(minutes * 60))

    # distribute times roughly
    per_line = max(1, total_seconds / len(lines))
    srt_lines = []
    start = 0.0
    idx = 1
    for l in lines:
        end = start + per_line
        srt_lines.append(f"{idx}\n{_format_time(start)} --> {_format_time(end)}\n{l}\n")
        start = end
        idx += 1

    out = TMP / f"subs_{int(Path(__file__).stat().st_mtime)}.srt"
    out.write_text("\n".join(srt_lines), encoding="utf-8")
    log.info("Wrote subtitles: %s", out)
    return str(out)
