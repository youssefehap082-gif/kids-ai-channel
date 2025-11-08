#!/usr/bin/env python3
# scripts/generate_thumbnail.py
import os, json, subprocess
from pathlib import Path

OUT = Path("output")
manifest = OUT / ".build_manifest.json"
if not manifest.exists():
    print("Missing build manifest")
    raise SystemExit(1)
data = json.load(open(manifest, encoding="utf-8"))
files = data.get("files",[])
if not files:
    print("No files in manifest")
    raise SystemExit(1)
final = OUT / files[0]
thumb = OUT / "thumbnail.jpg"
# capture frame at 10s or middle
import math
def get_duration(p):
    try:
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(p)], stderr=subprocess.DEVNULL)
        return float(out.strip())
    except:
        return 0.0
dur = get_duration(final)
t = min(10, dur/2) if dur>0 else 2
subprocess.run(["ffmpeg","-y","-ss", str(t), "-i", str(final), "-vframes","1","-q:v","2", str(thumb)], check=True)
print("Created thumbnail:", thumb.name)
