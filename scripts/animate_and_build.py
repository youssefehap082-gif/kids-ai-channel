# scripts/animate_and_build.py
import json, os, subprocess, math, shutil
from pathlib import Path

OUT=Path("output")
ASSETS=Path("assets")
OUT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

script = json.load(open(OUT/"script.json", encoding="utf-8"))
scenes = script.get("scenes", [])

FPS = 24

def make_scene(idx, scene):
    bg = ASSETS / f"scene{idx}_bg.png"
    audio = OUT / f"scene{idx}.mp3"
    if not bg.exists():
        print("Missing background", bg, "-> skipping scene", idx)
        return None
    # estimate duration from text length if no audio
    if audio.exists():
        # get duration using ffprobe
        try:
            cmd = ["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(audio)]
            dur = float(subprocess.check_output(cmd).strip())
        except Exception:
            dur = max(6.0, min(20.0, len(scene.get("text",""))/10.0 + 3.0))
    else:
        dur = max(6.0, min(20.0, len(scene.get("text",""))/10.0 + 3.0))
    print(f"Scene {idx}: duration {dur:.2f}s")
    frames = int(math.ceil(dur * FPS))
    tmp = OUT / f"scene{idx}_tmp.mp4"
    final = OUT / f"scene{idx}_final.mp4"
    # use zoompan (Ken Burns)
    zoom_expr = "zoom+0.0009"
    cmd = [
        "ffmpeg","-y","-loop","1","-i", str(bg),
        "-vf", f"zoompan=z='{zoom_expr}':d={frames}:s=1280x720,framerate={FPS}",
        "-t", str(dur), "-c:v","libx264","-pix_fmt","yuv420p", str(tmp)
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    # combine audio if present
    if audio.exists():
        cmd2 = ["ffmpeg","-y","-i", str(tmp), "-i", str(audio), "-c:v","copy","-c:a","aac","-b:a","192k", str(final)]
    else:
        cmd2 = ["ffmpeg","-y","-i", str(tmp), "-c:v","copy", str(final)]
    subprocess.run(cmd2, check=True)
    # cleanup
    tmp.unlink(missing_ok=True)
    return final

scene_files = []
for s in scenes:
    idx = s.get("idx")
    out = make_scene(idx, s)
    if out:
        scene_files.append(out)

if not scene_files:
    print("No scene files created. Exiting.")
    raise SystemExit(1)

# write list file relative to OUT
list_file = OUT / "mylist.txt"
with open(list_file, "w", encoding="utf-8") as f:
    for p in scene_files:
        f.write(f"file '{p.name}'\n")

# concat from within OUT
cwd = os.getcwd()
os.chdir(str(OUT))
try:
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i","mylist.txt","-c","copy","final_episode.mp4"], check=True)
    print("Built final_episode.mp4")
    # create short first 120s (re-encode to be safe)
    subprocess.run(["ffmpeg","-y","-i","final_episode.mp4","-ss","0","-t","120","-c:v","libx264","-c:a","aac","short_episode.mp4"], check=True)
    print("Built short_episode.mp4")
finally:
    os.chdir(cwd)
