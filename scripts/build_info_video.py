#!/usr/bin/env python3
# scripts/build_info_video.py
# Compose per-scene clips into final info video, sync with per-scene audio
import os, json, subprocess, shlex
from pathlib import Path

OUT = Path("output")
CLIPS = Path("clips")
OUT.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)

script_path = OUT / "script.json"
if not script_path.exists():
    print("Missing output/script.json")
    raise SystemExit(1)

script = json.load(open(script_path, encoding="utf-8"))
scenes = script.get("scenes", [])
title = script.get("title","Animal Facts")
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

scene_videos = []
audio_list = []
for s in scenes:
    idx = s["idx"]
    clip = CLIPS / f"scene_{idx}.mp4"
    audio = OUT / f"scene_{idx}.mp3"
    if not clip.exists():
        print(f"[WARN] clip missing for scene {idx}, creating color fallback 6s")
        # fallback short color
        clip = OUT / f"fallback_scene_{idx}.mp4"
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=0x2b2b3a:s=1280x720:d=6","-c:v","libx264","-pix_fmt","yuv420p", str(clip)], check=True)
    # overlay caption text (headline or short text)
    caption = s.get("headline","")
    # safe caption for drawtext (escape single quotes)
    caption_safe = caption.replace("'", r"\'")
    styled = OUT / f"scene_{idx}_styled.mp4"
    draw = f"drawtext=fontfile={font}:text='{caption_safe}':fontcolor=white:fontsize=36:box=1:boxcolor=0x00000099:boxborderw=8:x=(w-text_w)/2:y=h-110"
    subprocess.run(["ffmpeg","-y","-i", str(clip), "-vf", draw, "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(styled)], check=True)
    # ensure styled duration equals audio duration (trim/pad)
    # get audio duration
    adur = None
    try:
        adur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(audio)]).strip())
    except:
        adur = None
    if adur:
        trimmed = OUT / f"scene_{idx}_final.mp4"
        subprocess.run(["ffmpeg","-y","-ss","0","-i", str(styled), "-t", str(adur), "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(trimmed)], check=True)
    else:
        trimmed = styled
    scene_videos.append(trimmed)
    if audio.exists():
        audio_list.append(audio)
# concat scenes videos
if not scene_videos:
    print("[ERROR] No scene videos built")
    raise SystemExit(1)
# create list file
listf = OUT / "scene_vlist.txt"
with open(listf, "w", encoding="utf-8") as f:
    for p in scene_videos:
        f.write(f"file '{p.resolve()}'\n")
final_tmp = OUT / "info_concat_tmp.mp4"
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(final_tmp)], check=True)
# concat audio files
if audio_list:
    alistf = OUT / "audio_concat.txt"
    with open(alistf, "w", encoding="utf-8") as f:
        for a in audio_list:
            f.write(f"file '{a.resolve()}'\n")
    final_audio = OUT / "narration_full.mp3"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(alistf), "-c","copy", str(final_audio)], check=True)
    # mux audio with video
    final_info = OUT / f"final_{script.get('animal_key')}_info.mp4"
    subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-i", str(final_audio), "-c:v","copy","-c:a","aac","-b:a","192k", str(final_info)], check=True)
else:
    final_info = OUT / f"final_{script.get('animal_key')}_info.mp4"
    # move tmp to final
    subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-c","copy", str(final_info)], check=True)

print("Built info video:", final_info)
# Create short version <=120s
short = OUT / f"short_{script.get('animal_key')}_info.mp4"
subprocess.run(["ffmpeg","-y","-i", str(final_info), "-ss","0","-t","120","-c","copy", str(short)], check=False)
print("Also created short:", short)
# write manifest
manifest = {"files":[final_info.name, short.name]}
open(OUT / ".build_manifest.json","w",encoding="utf-8").write(json.dumps(manifest, indent=2))
print("Wrote manifest .build_manifest.json")
