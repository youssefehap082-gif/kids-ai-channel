# scripts/build_animal_video.py
import os, json, subprocess, math, random, shutil
from pathlib import Path

OUT = Path("output")
CLIPS = Path("clips")
ASSETS_MUSIC = Path("assets/music")
OUT.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)
ASSETS_MUSIC.mkdir(parents=True, exist_ok=True)

script = json.load(open(OUT/"script.json", encoding="utf-8"))
scenes = script.get("scenes", [])
animal_key = script.get("animal_key", "animal")
title_base = script.get("title", f"All About {animal_key}")

narration = OUT / "narration.mp3"

def get_duration(path):
    try:
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                       "-of","default=noprint_wrappers=1:nokey=1", str(path)])
        return float(out.strip())
    except:
        return None

# ---- 1) Prepare styled trimmed clips for the info video ----
clip_length = 25  # seconds per scene -> total depends on number of scenes
styled_files = []
for s in scenes:
    idx = s.get("idx")
    src = CLIPS / f"clip{idx}.mp4"
    if not src.exists():
        print("Missing clip", src, "— skipping")
        continue
    trimmed = OUT / f"clip{idx}_trim.mp4"
    # trim
    cmd_trim = [
        "ffmpeg","-y","-ss","0","-i", str(src),
        "-t", str(clip_length),
        "-vf", "scale=1280:720,setsar=1",
        "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k",
        str(trimmed)
    ]
    subprocess.run(cmd_trim, check=True)
    # overlay caption
    caption = s.get("caption","")
    # escape single quotes for shell drawtext
    caption_safe = caption.replace("'", r"\'").replace(":", r'\:')
    styled = OUT / f"clip{idx}_styled.mp4"
    drawtext = f"drawtext=text='{caption_safe}':fontcolor=white:fontsize=36:box=1:boxcolor=0x00000099:boxborderw=10:x=(w-text_w)/2:y=h-120"
    cmd_draw = ["ffmpeg","-y","-i", str(trimmed), "-vf", drawtext,
                "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(styled)]
    subprocess.run(cmd_draw, check=True)
    styled_files.append(styled)

if not styled_files:
    print("No clips prepared for info video — aborting info video.")
else:
    # concat
    listf = OUT / "info_list.txt"
    with open(listf, "w", encoding="utf-8") as f:
        for p in styled_files:
            f.write(f"file '{p.resolve()}'\n")
    final_tmp = OUT / "info_tmp.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(final_tmp)], check=True)
    # mix narration
    final_info = OUT / f"final_{animal_key}_info.mp4"
    if narration.exists():
        vdur = get_duration(final_tmp) or 0
        adur = get_duration(narration) or 0
        temp_audio = OUT / "narr_loop.mp3"
        if adur < vdur and adur>0:
            subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(narration), "-t", str(vdur), "-c","aac", str(temp_audio)], check=True)
            audio_in = temp_audio
        elif adur>0:
            subprocess.run(["ffmpeg","-y","-ss","0","-i", str(narration), "-t", str(vdur), "-c","copy", str(temp_audio)], check=True)
            audio_in = temp_audio
        else:
            audio_in = None
        if audio_in:
            subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-i", str(audio_in), "-c:v","copy","-c:a","aac","-b:a","192k", str(final_info)], check=True)
            try:
                temp_audio.unlink()
            except:
                pass
        else:
            # no valid audio, just move
            shutil.move(str(final_tmp), str(final_info))
    else:
        shutil.move(str(final_tmp), str(final_info))
    print("Built info video:", final_info)

# ---- 2) Build 2 ambient videos (5-10 minutes) without narration but with different music ----
# For ambient videos we want longer output: pick some clips and loop/concatenate them to reach target duration.
def build_ambient(kind_idx, target_minutes=7):
    # choose animal clips: pick from all downloaded clips; if not enough use generic query clips
    available = sorted(CLIPS.glob("clip*.mp4"))
    if not available:
        print("No available clips for ambient video", kind_idx)
        return None
    target_seconds = int(target_minutes * 60)
    segments = []
    cur_dur = 0
    # randomly pick clips and trim/loop until reach target
    idx = 0
    while cur_dur < target_seconds:
        src = available[idx % len(available)]
        seg_out = OUT / f"ambient_k{kind_idx}_seg{idx}.mp4"
        seg_len = min(60, target_seconds - cur_dur)  # take up to 60s from each clip to vary
        cmd = ["ffmpeg","-y","-ss","0","-i", str(src), "-t", str(seg_len), "-vf", "scale=1280:720,setsar=1",
               "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(seg_out)]
        subprocess.run(cmd, check=True)
        segments.append(seg_out)
        cur_dur += seg_len
        idx += 1
    # concat segments
    listf = OUT / f"ambient_k{kind_idx}_list.txt"
    with open(listf, "w", encoding="utf-8") as f:
        for p in segments:
            f.write(f"file '{p.resolve()}'\n")
    tmp = OUT / f"ambient_k{kind_idx}_tmp.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(tmp)], check=True)
    # pick a music file from assets/music randomly if exists
    music_files = list(ASSETS_MUSIC.glob("*.mp3")) + list(ASSETS_MUSIC.glob("*.wav"))
    final = OUT / f"ambient_{animal_key}_{kind_idx}.mp4"
    if music_files:
        music = random.choice(music_files)
        # loop or trim music to match duration
        vdur = get_duration(tmp) or 0
        if vdur <= 0:
            shutil.move(str(tmp), str(final))
            return final
        music_tmp = OUT / f"ambient_k{kind_idx}_music_loop.mp3"
        adur = get_duration(music) or 0
        if adur < vdur and adur>0:
            subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(music), "-t", str(vdur), "-c","aac", str(music_tmp)], check=True)
        else:
            subprocess.run(["ffmpeg","-y","-ss","0","-i", str(music), "-t", str(vdur), "-c","copy", str(music_tmp)], check=True)
        subprocess.run(["ffmpeg","-y","-i", str(tmp), "-i", str(music_tmp), "-c:v","copy","-c:a","aac","-b:a","192k", str(final)], check=True)
        try:
            music_tmp.unlink()
        except:
            pass
    else:
        # no music, keep silent video
        shutil.move(str(tmp), str(final))
    # cleanup segments
    for p in segments:
        try:
            p.unlink()
        except:
            pass
    try:
        listf.unlink()
    except:
        pass
    print("Built ambient video:", final)
    return final

ambient1 = build_ambient(1, target_minutes=7)  # ~7 minutes
ambient2 = build_ambient(2, target_minutes=6)  # ~6 minutes (different length to vary)

# Done - print final files
print("Outputs in output/:")
for f in sorted(OUT.glob("*.mp4")):
    print(" -", f.name)
