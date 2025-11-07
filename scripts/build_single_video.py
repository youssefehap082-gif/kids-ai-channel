# scripts/build_single_video.py
import os, json, subprocess, math, random, shutil
from pathlib import Path

MODE = os.environ.get("MODE","info")
OUT = Path("output")
CLIPS = Path("clips")
ASSETS_MUSIC = Path("assets/music")
OUT.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)

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

if MODE == "info":
    print("Building INFO video with narration.")
    # Build short concatenated styled clips
    clip_length = 25
    styled_files = []
    for s in scenes:
        idx = s.get("idx")
        src = CLIPS / f"clip{idx}.mp4"
        if not src.exists():
            print("Missing clip", src, "— skipping")
            continue
        trimmed = OUT / f"clip{idx}_trim.mp4"
        subprocess.run(["ffmpeg","-y","-ss","0","-i", str(src), "-t", str(clip_length),
                        "-vf", "scale=1280:720,setsar=1","-c:v","libx264","-preset","fast",
                        "-c:a","aac","-b:a","128k", str(trimmed)], check=True)
        caption = s.get("caption","")
        caption_safe = caption.replace("'", r"\'").replace(":", r'\:')
        styled = OUT / f"clip{idx}_styled.mp4"
        drawtext = f"drawtext=text='{caption_safe}':fontcolor=white:fontsize=36:box=1:boxcolor=0x00000099:boxborderw=10:x=(w-text_w)/2:y=h-120"
        subprocess.run(["ffmpeg","-y","-i", str(trimmed), "-vf", drawtext,
                        "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(styled)], check=True)
        styled_files.append(styled)
    if not styled_files:
        print("No styled clips — cannot build info video.")
    else:
        listf = OUT / "info_list.txt"
        with open(listf, "w", encoding="utf-8") as f:
            for p in styled_files:
                f.write(f"file '{p.resolve()}'\n")
        final_tmp = OUT / "info_tmp.mp4"
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(final_tmp)], check=True)
        final_info = OUT / f"final_{animal_key}_info.mp4"
        if narration.exists():
            vdur = get_duration(final_tmp) or 0
            adur = get_duration(narration) or 0
            temp_audio = OUT / "narr_loop.mp3"
            if adur > 0 and adur < vdur:
                subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(narration), "-t", str(vdur), "-c","aac", str(temp_audio)], check=True)
                audio_in = temp_audio
            elif adur > 0:
                subprocess.run(["ffmpeg","-y","-ss","0","-i", str(narration), "-t", str(vdur), "-c","copy", str(temp_audio)], check=True)
                audio_in = temp_audio
            else:
                audio_in = None
            if audio_in:
                subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-i", str(audio_in), "-c:v","copy","-c:a","aac","-b:a","192k", str(final_info)], check=True)
                try: temp_audio.unlink()
                except: pass
            else:
                shutil.move(str(final_tmp), str(final_info))
        else:
            shutil.move(str(final_tmp), str(final_info))
        print("Built info video:", final_info)
        # build short <=120s
        short = OUT / f"short_{animal_key}_info.mp4"
        subprocess.run(["ffmpeg","-y","-i", str(final_info), "-ss","0","-t","120","-c:v","libx264","-c:a","aac", str(short)], check=True)
        print("Built short:", short)

else:
    # Ambient mode: build 1 ambient video ~7 minutes with music
    print("Building AMBIENT video (no narration, music background if available).")
    available = sorted(CLIPS.glob("clip*.mp4"))
    if not available:
        print("No clips available to build ambient video.")
    else:
        target_minutes = 7
        target_seconds = int(target_minutes * 60)
        segments = []
        cur_dur = 0
        idx = 0
        while cur_dur < target_seconds:
            src = available[idx % len(available)]
            seg_out = OUT / f"ambient_seg_{idx}.mp4"
            seg_len = min(60, target_seconds - cur_dur)
            subprocess.run(["ffmpeg","-y","-ss","0","-i", str(src), "-t", str(seg_len),
                            "-vf","scale=1280:720,setsar=1","-c:v","libx264","-preset","fast",
                            "-c:a","aac","-b:a","128k", str(seg_out)], check=True)
            segments.append(seg_out)
            cur_dur += seg_len
            idx += 1
        listf = OUT / "ambient_list.txt"
        with open(listf, "w", encoding="utf-8") as f:
            for p in segments:
                f.write(f"file '{p.resolve()}'\n")
        tmp = OUT / f"ambient_{animal_key}_tmp.mp4"
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(tmp)], check=True)
        # choose music file if available
        music_files = list(ASSETS_MUSIC.glob("*.mp3")) + list(ASSETS_MUSIC.glob("*.wav"))
        final = OUT / f"ambient_{animal_key}.mp4"
        if music_files:
            music = random.choice(music_files)
            vdur = get_duration(tmp) or 0
            if vdur > 0:
                music_tmp = OUT / f"ambient_music_loop.mp3"
                adur = get_duration(music) or 0
                if adur > 0 and adur < vdur:
                    subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(music), "-t", str(vdur), "-c","aac", str(music_tmp)], check=True)
                else:
                    subprocess.run(["ffmpeg","-y","-ss","0","-i", str(music), "-t", str(vdur), "-c","copy", str(music_tmp)], check=True)
                subprocess.run(["ffmpeg","-y","-i", str(tmp), "-i", str(music_tmp), "-c:v","copy","-c:a","aac","-b:a","192k", str(final)], check=True)
                try: music_tmp.unlink()
                except: pass
            else:
                shutil.move(str(tmp), str(final))
        else:
            # no music - keep silent ambient
            shutil.move(str(tmp), str(final))
        # cleanup segment files
        for p in segments:
            try: p.unlink()
            except: pass
        try: listf.unlink()
        except: pass
        print("Built ambient video:", final)
        # build short podcast (<120s) for Shorts if desired
        short = OUT / f"short_{animal_key}_ambient.mp4"
        subprocess.run(["ffmpeg","-y","-i", str(final), "-ss","0","-t","120","-c:v","libx264","-c:a","aac", str(short)], check=True)
        print("Built ambient short:", short)
