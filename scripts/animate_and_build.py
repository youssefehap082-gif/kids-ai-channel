# scripts/animate_and_build.py
import json, os, subprocess, math
from pathlib import Path
OUT=Path("output")
ASSETS=Path("assets")
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)

# load script
script = json.load(open(OUT/"script.json", encoding="utf-8"))
scenes = script.get("scenes",[])
FPS=24

def make_scene_video(idx, scene, out_mp4):
    bg = ASSETS / f"scene{idx}_bg.png"
    if not bg.exists():
        print("Missing background", bg, "-> skipping")
        return False
    # assemble dialogue into subtitles.srt for this scene
    # estimate duration per line ~ 3-5s; we will set scene duration = sum of estimated durations + margin
    lines = scene.get("dialogue",[])
    est = 0
    subs = []
    cur = 0.5
    for i,l in enumerate(lines, start=1):
        text = l.get("text","").strip()
        dur = max(3.0, min(8.0, len(text)/10.0 + 1.5))  # crude estimate
        start = cur
        end = cur + dur
        cur = end + 0.4
        est += dur
        # srt index, time format
        def fmt(t):
            h=int(t//3600); m=int((t%3600)//60); s=int(t%60); ms=int((t*1000)%1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        subs.append((i, fmt(start), fmt(end), text))
    scene_duration = max(5.0, est + 1.0)
    # write srt
    srt_path = OUT / f"scene{idx}.srt"
    with open(srt_path,"w",encoding="utf-8") as f:
        for ii, a, b, text in subs:
            f.write(f"{ii}\n{a} --> {b}\n{text}\n\n")

    # create moving video from image using ffmpeg zoompan (Ken Burns)
    tmp_video = OUT / f"scene{idx}_tmp.mp4"
    # Use zoompan to slowly zoom in and out slightly
    zoom_expr = "zoom+0.0008"
    frames = int(math.ceil(scene_duration * FPS))
    cmd = [
        "ffmpeg","-y","-loop","1","-i", str(bg),
        "-vf", f"zoompan=z='{zoom_expr}':d={frames}:s=1280x720,framerate={FPS}:interp_start=0:interp_end=255",
        "-t", str(scene_duration), "-c:v","libx264","-pix_fmt","yuv420p", str(tmp_video)
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # burn subtitles into video
    scene_with_subs = OUT / f"scene{idx}.mp4"
    cmd2 = [
      "ffmpeg","-y","-i", str(tmp_video), "-vf", f"subtitles={str(srt_path)}:force_style='FontName=Arial,FontSize=24,Outline=1,Shadow=1'",
      "-c:v","libx264","-c:a","aac","-shortest", str(scene_with_subs)
    ]
    subprocess.run(cmd2, check=True)
    # cleanup tmp
    tmp_video.unlink(missing_ok=True)
    srt_path.unlink(missing_ok=True)
    return True

# make each scene video
scene_files=[]
for idx, sc in enumerate(scenes, start=1):
    out_mp4 = OUT / f"scene{idx}_final.mp4"
    ok = make_scene_video(idx, sc, out_mp4)
    if ok:
        scene_files.append(out_mp4)

if not scene_files:
    print("No scenes produced.")
    raise SystemExit(1)

# concatenate
list_file = OUT / "mylist.txt"
with open(list_file,"w",encoding="utf-8") as f:
    for p in scene_files:
        f.write(f"file '{p.name}'\n")
# run concat inside OUT
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(list_file), "-c","copy", str(OUT/"final_episode.mp4")], check=True)
print("Built final_episode.mp4")

# make short (first 120s)
subprocess.run(["ffmpeg","-y","-i", str(OUT/"final_episode.mp4"), "-ss","0","-t","120","-c","copy", str(OUT/"short_episode.mp4")], check=True)
print("Built short_episode.mp4")
