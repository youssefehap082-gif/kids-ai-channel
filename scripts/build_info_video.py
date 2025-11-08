#!/usr/bin/env python3
# scripts/build_info_video.py
import os, json, subprocess
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
animal = script.get("animal_key","animal")
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

scene_videos = []
audio_list = []
for s in scenes:
    idx = s["idx"]
    clip = CLIPS / f"scene_{idx}.mp4"
    audio = OUT / f"scene_{idx}.mp3"
    if not clip.exists():
        print(f"[WARN] clip missing for scene {idx}, creating color fallback")
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x11121a:s=1280x720:d=6","-c:v","libx264","-pix_fmt","yuv420p", str(clip)], check=True)
    caption = s.get("headline","")
    caption_safe = caption.replace("'", r"\'")
    styled = OUT / f"scene_{idx}_styled.mp4"
    # draw headline at bottom
    draw = f"drawtext=fontfile={font}:text='{caption_safe}':fontcolor=white:fontsize=30:box=1:boxcolor=0x00000099:boxborderw=8:x=(w-text_w)/2:y=h-100"
    subprocess.run(["ffmpeg","-y","-i", str(clip), "-vf", draw, "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(styled)], check=True)
    # align duration to audio if audio exists
    adur = None
    if audio.exists():
        try:
            out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(audio)])
            adur = float(out.strip())
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

# concat scenes
if not scene_videos:
    print("[ERROR] No scene videos built")
    raise SystemExit(1)

listf = OUT / "scene_vlist.txt"
with open(listf, "w", encoding="utf-8") as f:
    for p in scene_videos:
        f.write(f"file '{p.resolve()}'\n")

final_tmp = OUT / "info_concat_tmp.mp4"
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(final_tmp)], check=True)

if audio_list:
    alistf = OUT / "audio_concat.txt"
    with open(alistf, "w", encoding="utf-8") as f:
        for a in audio_list:
            f.write(f"file '{a.resolve()}'\n")
    final_audio = OUT / "narration_full.mp3"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(alistf), "-c","copy", str(final_audio)], check=True)
    final_info = OUT / f"final_{animal}_info.mp4"
    subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-i", str(final_audio), "-c:v","copy","-c:a","aac","-b:a","192k", str(final_info)], check=True)
else:
    final_info = OUT / f"final_{animal}_info.mp4"
    subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-c","copy", str(final_info)], check=True)

# short <= 120s
short = OUT / f"short_{animal}_info.mp4"
subprocess.run(["ffmpeg","-y","-i", str(final_info), "-ss","0","-t","120","-c","copy", str(short)], check=False)

manifest = {"files":[final_info.name, short.name]}
open(OUT / ".build_manifest.json","w",encoding="utf-8").write(json.dumps(manifest, indent=2))
print("Built", final_info.name)
