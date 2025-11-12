# src/helpers.py
import re
import datetime

def split_text_for_srt(text, max_chars=40):
    # split text to segments roughly max_chars
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def generate_srt_from_text(text, duration_seconds):
    lines = split_text_for_srt(text, max_chars=40)
    per = duration_seconds / max(len(lines),1)
    srt = ""
    for i, line in enumerate(lines):
        start = datetime.timedelta(seconds=int(i*per))
        end = datetime.timedelta(seconds=int((i+1)*per))
        # format HH:MM:SS,mmm
        def fmt(td):
            total = int(td.total_seconds())
            h = total//3600
            m = (total%3600)//60
            s = total%60
            return f"{h:02d}:{m:02d}:{s:02d},000"
        srt += f"{i+1}\n{fmt(start)} --> {fmt(end)}\n{line}\n\n"
    return srt
