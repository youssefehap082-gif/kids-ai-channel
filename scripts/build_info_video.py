#!/usr/bin/env python3
# scripts/build_info_video.py
import os, json, subprocess, shlex, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
CLIPS = ROOT / "clips"
OUT.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)

def run(cmd):
    print("RUN:", cmd)
    subprocess.run(cmd, shell=True, check=True)

def get_dur(p):
    try:
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(p)], stderr=subprocess.DEVNULL)
        return float(out.strip())
    except:
        return 0.0

script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json")
    raise SystemExit(1)
script = json.load(open(script_path, encoding="utf-8"))
animal = script.get("animal_key","animal")
combined = CLIPS / "combined_clips.mp4"
if not combined.exists():
    print("Missing combined_clips.mp4")
    raise SystemExit(1)
narration = OUT / "narration_full.mp3"
narr_dur = get_dur(narration) if narration.exists() else 0.0
video_dur = get_dur(combined)
# if narration > video -> loop last segment
if narr_dur > video_dur:
    extra = narr_dur - video_dur
    last_seg = CLIPS / "lastseg.mp4"
    run(f"ffmpeg -y -ss {max(0, video_dur-10)} -i {shlex.quote(str(combined))} -t 10 -c copy {shlex.quote(str(last_seg))}")
    repeats = int(math.ceil(extra / 10.0))
    listf = CLIPS / "extend_list.txt"
    with open(listf,"w",encoding="utf-8") as f:
        f.write(f"file '{combined.resolve()}'\n")
        for i in range(repeats):
            cp = CLIPS / f"extend_{i}.mp4"
            run(f"cp {shlex.quote(str(last_seg))} {shlex.quote(str(cp))}")
            f.write(f"file '{cp.resolve()}'\n")
    extended = CLIPS / "combined_extended.mp4"
    run(f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(listf))} -c copy {shlex.quote(str(extended))}")
    combined = extended

final = OUT / f"final_{animal}_info.mp4"
if narration.exists():
    run(f"ffmpeg -y -i {shlex.quote(str(combined))} -i {shlex.quote(str(narration))} -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest {shlex.quote(str(final))}")
else:
    run(f"ffmpeg -y -i {shlex.quote(str(combined))} -c copy {shlex.quote(str(final))}")

# ensure minimum duration 180
final_dur = get_dur(final)
if final_dur < 180:
    extra = 180 - final_dur
    pad = OUT / "pad.mp4"
    run(f"ffmpeg -y -f lavfi -i color=c=0x0f2130:s=1280x720:d={extra} -c:v libx264 -pix_fmt yuv420p {shlex.quote(str(pad))}")
    listf = OUT / "final_list.txt"
    with open(listf,"w",encoding="utf-8") as f:
        f.write(f"file '{final.resolve()}'\n")
        f.write(f"file '{pad.resolve()}'\n")
    padded = OUT / f"final_{animal}_info_padded.mp4"
    run(f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(listf))} -c copy {shlex.quote(str(padded))}")
    final = padded

# short <= 120s
short = OUT / f"short_{animal}_info.mp4"
run(f"ffmpeg -y -i {shlex.quote(str(final))} -ss 0 -t 120 -c copy {shlex.quote(str(short))}")

manifest = {"files":[final.name, short.name], "title": script.get("title"), "description": script.get("description"), "tags": script.get("tags",[])}
open(OUT / ".build_manifest.json","w",encoding="utf-8").write(json.dumps(manifest, indent=2))
print("Built final video:", final.name)
