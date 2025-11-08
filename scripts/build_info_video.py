#!/usr/bin/env python3
# scripts/build_info_video.py
# Use clips/combined_clips.mp4 (created by download_and_prepare_clips.py) and
# output/narration_full.mp3 to produce final video with minimum duration requirement.

import os, json, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
CLIPS = ROOT / "clips"
OUT.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)

def run(cmd):
    print("RUN:", cmd)
    subprocess.run(cmd, shell=True, check=True)

def get_duration(path):
    try:
        out = subprocess.check_output([
            "ffprobe","-v","error","-show_entries","format=duration",
            "-of","default=noprint_wrappers=1:nokey=1", str(path)], stderr=subprocess.DEVNULL)
        return float(out.strip())
    except Exception:
        return 0.0

script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json")
    raise SystemExit(1)

script = json.load(open(script_path, encoding="utf-8"))
animal = script.get("animal_key","animal")

combined = CLIPS / "combined_clips.mp4"
if not combined.exists():
    print("Combined clips not found. Run download_and_prepare_clips.py first.")
    raise SystemExit(1)

narration = OUT / "narration_full.mp3"
narr_dur = get_duration(narration) if narration.exists() else 0.0
video_dur = get_duration(combined)

# If narration longer than video (shouldn't happen because download targeted max(narration,MIN))
if narr_dur > video_dur:
    print(f"[INFO] narration ({narr_dur:.1f}s) longer than video ({video_dur:.1f}s) — extending video by looping last 10s.")
    # extract last 10s of combined and loop it to match difference
    diff = narr_dur - video_dur
    last_seg = CLIPS / "combined_lastseg.mp4"
    run(f"ffmpeg -y -ss {max(0, video_dur-10)} -i {shlex.quote(str(combined))} -t 10 -c copy {shlex.quote(str(last_seg))}")
    # loop it ceil(diff/10) times, concat
    repeats = int(math.ceil(diff / 10.0))
    loop_parts = []
    for i in range(repeats):
        cp = CLIPS / f"loop_{i}.mp4"
        run(f"cp {shlex.quote(str(last_seg))} {shlex.quote(str(cp))}")
        loop_parts.append(cp)
    listf = CLIPS / "loop_list.txt"
    with open(listf, "w", encoding="utf-8") as f:
        f.write(f"file '{combined.resolve()}'\n")
        for p in loop_parts:
            f.write(f"file '{p.resolve()}'\n")
    extended = CLIPS / "combined_extended.mp4"
    run(f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(listf))} -c copy {shlex.quote(str(extended))}")
    combined = extended
    video_dur = get_duration(combined)

final_video = OUT / f"final_{animal}_info.mp4"

# Mux narration audio (if exists) with combined video. If audio shorter than video, we still mux it.
if narration.exists():
    run(f"ffmpeg -y -i {shlex.quote(str(combined))} -i {shlex.quote(str(narration))} -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest {shlex.quote(str(final_video))}")
else:
    # no narration, just copy combined
    run(f"ffmpeg -y -i {shlex.quote(str(combined))} -c copy {shlex.quote(str(final_video))}")

# ensure final duration >= 180 (some safety)
final_dur = get_duration(final_video)
if final_dur < 180:
    print(f"[WARN] final video {final_dur}s < 180s, padding with color to reach 180s")
    pad = OUT / f"final_{animal}_info_padded.mp4"
    extra = 180 - final_dur
    run(f"ffmpeg -y -f lavfi -i color=c=0x0f2130:s=1280x720:d={extra} -c:v libx264 -pix_fmt yuv420p {shlex.quote(str(OUT/'pad_tmp.mp4'))}")
    # concat final_video + pad
    listf = OUT / "final_concat_list.txt"
    with open(listf, "w", encoding="utf-8") as f:
        f.write(f"file '{final_video.resolve()}'\n")
        f.write(f"file '{(OUT/'pad_tmp.mp4').resolve()}'\n")
    run(f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(listf))} -c copy {shlex.quote(str(pad))}")
    pad.unlink(missing_ok=True)
    (OUT/'pad_tmp.mp4').unlink(missing_ok=True)
    final_video = pad

# create short version for shorts/reels (<=120s)
short_out = OUT / f"short_{animal}_info.mp4"
run(f"ffmpeg -y -i {shlex.quote(str(final_video))} -ss 0 -t 120 -c copy {shlex.quote(str(short_out))}")

# write manifest
manifest = {"files":[final_video.name, short_out.name]}
open(OUT / ".build_manifest.json", "w", encoding="utf-8").write(json.dumps(manifest, indent=2))
print("Built final:", final_video.name)
