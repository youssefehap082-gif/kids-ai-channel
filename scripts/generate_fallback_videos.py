#!/usr/bin/env python3
# scripts/generate_fallback_videos.py
# Create fallback videos (text-on-color) into output/ if real video assets are missing.
# Uses ffmpeg drawtext. Produces 3 "info" videos and 2 "ambient" videos from output/script.json.
# Durations safe: info ~120s, ambient ~300s (can be adjusted).

import os, json, subprocess, shlex
from pathlib import Path
OUT = Path("output")
OUT.mkdir(parents=True, exist_ok=True)

def run(cmd):
    print("RUN:", cmd)
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print("Command failed:", res.returncode)
    return res.returncode

# read script.json if exists
script = {}
if (OUT / "script.json").exists():
    try:
        script = json.load(open(OUT / "script.json", encoding="utf-8"))
    except Exception as e:
        print("Failed parsing script.json:", e)
else:
    print("Warning: output/script.json not found — will create generic fallback videos.")

title = script.get("title", "Animal Facts")
scenes = script.get("scenes", [])
animal_key = script.get("animal_key", "animal")

# helper to build a single info fallback video
def make_info_fallback(idx, duration=120):
    outv = OUT / f"final_fallback_info_{idx}.mp4"
    text_lines = []
    if scenes:
        # join some scene texts (max 6 lines)
        for s in scenes[:6]:
            t = s.get("headline","") + " - " + s.get("text","")
            text_lines.append(t)
    else:
        text_lines = [
            f"{title}",
            "Auto-generated fallback video",
            "Subscribe for more animal facts!"
        ]
    text = " | ".join(text_lines)
    # Use ffmpeg color + drawtext. Use DejaVuSans if available.
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not Path(font).exists():
        font = "Arial"
    # create video with centered text, gentle zoom simulated by scale filter
    cmd = (
        f"ffmpeg -y -f lavfi -i color=c=0x1e1e2f:s=1280x720:d={duration} "
        f"-vf \"drawtext=fontfile={font}:text='{text}':fontcolor=white:fontsize=28:box=1:boxcolor=0x00000088:boxborderw=10:x=(w-text_w)/2:y=(h-text_h)/2\" "
        f"-c:v libx264 -preset fast -pix_fmt yuv420p -r 24 {shlex.quote(str(outv))}"
    )
    run(cmd)
    print("Created fallback info:", outv.name)
    return outv

# helper to build ambient fallback video with repeated simple text
def make_ambient_fallback(idx, duration=300):
    outv = OUT / f"ambient_fallback_{idx}.mp4"
    text = f"{title} — Ambient Visuals (Fallback #{idx})"
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not Path(font).exists():
        font = "Arial"
    cmd = (
        f"ffmpeg -y -f lavfi -i color=c=0x0f3b53:s=1280x720:d={duration} "
        f"-vf \"drawtext=fontfile={font}:text='{text}':fontcolor=white:fontsize=36:box=1:boxcolor=0x00000077:boxborderw=8:x=(w-text_w)/2:y=h-100\" "
        f"-c:v libx264 -preset fast -pix_fmt yuv420p -r 24 {shlex.quote(str(outv))}"
    )
    run(cmd)
    print("Created fallback ambient:", outv.name)
    return outv

def main():
    # produce 3 info + 2 ambient fallback files
    created = []
    for i in range(1,4):
        created.append(make_info_fallback(i, duration=120))
    for j in range(1,3):
        created.append(make_ambient_fallback(j, duration=300))
    # write minimal manifest so uploader can pick them easily
    manifest = {"files":[p.name for p in created]}
    open(OUT / ".build_manifest.json", "w", encoding="utf-8").write(json.dumps(manifest, indent=2))
    print("Fallback manifest written:", (OUT / ".build_manifest.json").as_posix())
    print("Fallback generation done. Files created in output/:")
    for p in created:
        print(" -", p.name)

if __name__ == "__main__":
    import json
    main()
