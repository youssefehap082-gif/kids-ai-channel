# scripts/build_short.py
import os, json, subprocess, math
from pathlib import Path

OUT = Path("output")
CLIPS = Path("clips")
OUT.mkdir(parents=True, exist_ok=True)

script = json.load(open(OUT/"script.json", encoding="utf-8"))
scenes = script.get("scenes", [])
narration = OUT / "narration.mp3"

# target clip duration (sec) - adjust if narration shorter/longer
clip_dur = 12  # seconds per clip (3 clips => 36s)

temp_files = []
for s in scenes:
    idx = s["idx"]
    clip_src = CLIPS / f"clip{idx}.mp4"
    if not clip_src.exists():
        print("Missing clip", clip_src, "— skipping")
        continue
    trimmed = OUT / f"clip{idx}_trim.mp4"
    # trim or loop to required duration (use -t)
    cmd = [
        "ffmpeg","-y","-ss","0","-i", str(clip_src),
        "-t", str(clip_dur),
        "-vf", "scale=1280:720,setsar=1",
        "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k",
        str(trimmed)
    ]
    print("Trimming:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    # overlay caption text on trimmed (simple drawtext)
    caption = s.get("caption","")
    styled = OUT / f"clip{idx}_styled.mp4"
    # use drawtext; adjust font path if needed
    drawcmd = [
      "ffmpeg","-y","-i", str(trimmed),
      "-vf",
      f"drawtext=text='{caption}':fontcolor=white:fontsize=36:box=1:boxcolor=0x00000099:boxborderw=10:x=(w-text_w)/2:y=h-120",
      "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k",
      str(styled)
    ]
    subprocess.run(drawcmd, check=True)
    temp_files.append(styled)

# concat files
if not temp_files:
    print("No temp files created. Exiting.")
    raise SystemExit(1)

# create list file
listf = OUT / "mylist.txt"
with open(listf, "w", encoding="utf-8") as f:
    for t in temp_files:
        f.write(f"file '{t.resolve()}'\n")

final_tmp = OUT / "final_tmp.mp4"
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(final_tmp)], check=True)

# mix narration (if exists) — align duration by looping or trimming audio
final = OUT / "final_short.mp4"
if narration.exists():
    # if narration shorter than video, loop; if longer, cut
    # get video duration
    def get_duration(path):
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(path)])
        return float(out.strip())
    vdur = get_duration(final_tmp)
    adur = get_duration(narration)
    if adur < vdur:
        # loop audio: use -stream_loop
        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(narration), "-t", str(vdur), "-c:a","aac","temp_narr.mp3"], check=True)
        audio_in = "temp_narr.mp3"
    else:
        # trim audio
        subprocess.run(["ffmpeg","-y","-ss","0","-i", str(narration), "-t", str(vdur), "-c","copy","temp_narr.mp3"], check=True)
        audio_in = "temp_narr.mp3"
    # merge
    subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-i", audio_in, "-c:v","copy","-c:a","aac","-b:a","192k", str(final)], check=True)
    try:
        os.remove("temp_narr.mp3")
    except:
        pass
else:
    # no narration, just rename
    final_tmp.rename(final)

print("Final created:", final)
