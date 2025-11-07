# scripts/build_animal_video.py
import os, json, subprocess, math, shlex
from pathlib import Path
OUT = Path("output")
CLIPS = Path("clips")
OUT.mkdir(parents=True, exist_ok=True)

script = json.load(open(OUT/"script.json", encoding="utf-8"))
scenes = script.get("scenes", [])
narration = OUT / "narration.mp3"

# target per-clip seconds; total ~ (num_clips * clip_length)
clip_length = 25  # seconds per scene (adjustable) -> 6 scenes * 25 = 150s
styled_files = []

def ffmpeg_escape(text):
    # escape single quotes and backslashes for use inside single-quoted drawtext
    if text is None:
        return ""
    return text.replace("\\","\\\\").replace("'", r"\'").replace(":", r'\:')

for s in scenes:
    idx = s.get("idx")
    src = CLIPS / f"clip{idx}.mp4"
    if not src.exists():
        print("Missing clip", src, "— skipping")
        continue
    trimmed = OUT / f"clip{idx}_trim.mp4"
    # trim to clip_length
    cmd_trim = [
        "ffmpeg","-y","-ss","0","-i", str(src),
        "-t", str(clip_length),
        "-vf", "scale=1280:720,setsar=1",
        "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k",
        str(trimmed)
    ]
    print("Trim:", " ".join(cmd_trim))
    subprocess.run(cmd_trim, check=True)
    # overlay caption using drawtext (center bottom)
    caption = s.get("caption","")
    caption_safe = ffmpeg_escape(caption)
    styled = OUT / f"clip{idx}_styled.mp4"
    drawtext = f"drawtext=text='{caption_safe}':fontcolor=white:fontsize=36:box=1:boxcolor=0x00000099:boxborderw=10:x=(w-text_w)/2:y=h-120"
    cmd_draw = [
        "ffmpeg","-y","-i", str(trimmed),
        "-vf", drawtext,
        "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k",
        str(styled)
    ]
    subprocess.run(cmd_draw, check=True)
    styled_files.append(styled)

if not styled_files:
    print("No clips prepared — abort.")
    raise SystemExit(1)

# create list for concat (use absolute paths)
listf = OUT / "list.txt"
with open(listf, "w", encoding="utf-8") as f:
    for p in styled_files:
        f.write(f"file '{p.resolve()}'\n")

final_tmp = OUT / "final_tmp.mp4"
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(final_tmp)], check=True)

# mix narration with final_tmp -> final_animal.mp4
final = OUT / "final_animal.mp4"
def get_duration(path):
    out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                   "-of","default=noprint_wrappers=1:nokey=1", str(path)])
    return float(out.strip())

vdur = get_duration(final_tmp)
if narration.exists():
    adur = get_duration(narration)
    # if audio shorter -> loop, else trim
    temp_audio = OUT / "narr_loop.mp3"
    if adur < vdur:
        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(narration), "-t", str(vdur), "-c","aac", str(temp_audio)], check=True)
    else:
        subprocess.run(["ffmpeg","-y","-ss","0","-i", str(narration), "-t", str(vdur), "-c","copy", str(temp_audio)], check=True)
    subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-i", str(temp_audio), "-c:v","copy","-c:a","aac","-b:a","192k", str(final)], check=True)
    try:
        temp_audio.unlink()
    except:
        pass
else:
    final_tmp.rename(final)

print("Built final:", final)

# create short <= 120s (re-encode for safety)
short = OUT / "short_animal.mp4"
subprocess.run(["ffmpeg","-y","-i", str(final), "-ss","0","-t","120","-c:v","libx264","-c:a","aac", str(short)], check=True)
print("Built short:", short)
