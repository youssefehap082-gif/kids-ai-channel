#!/usr/bin/env python3
import math
def make_srt(lines, out_path):
    # lines: list of tuples (start_seconds, end_seconds, text)
    def fmt(t):
        h = int(t//3600)
        m = int((t%3600)//60)
        s = int(t%60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    with open(out_path, 'w', encoding='utf-8') as f:
        for i,(st,et,text) in enumerate(lines, start=1):
            f.write(str(i) + "\n")
            f.write(fmt(st) + " --> " + fmt(et) + "\n")
            f.write(text + "\n\n")
