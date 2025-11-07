# scripts/build_single_video.py (verbose + manifest)
import os, json, subprocess, random, shutil, time
from pathlib import Path

MODE = os.environ.get("MODE","info")
OUT = Path("output")
CLIPS = Path("clips")
ASSETS_MUSIC = Path("assets/music")
OUT.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)
ASSETS_MUSIC.mkdir(parents=True, exist_ok=True)

script_path = OUT / "script.json"
if not script_path.exists():
    print("[ERROR] output/script.json missing. Aborting build.")
    raise SystemExit(1)

script = json.load(open(script_path, encoding="utf-8"))
scenes = script.get("scenes", [])
animal_key = script.get("animal_key","animal")

def get_duration(path):
    try:
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                       "-of","default=noprint_wrappers=1:nokey=1", str(path)], stderr=subprocess.DEVNULL)
        return float(out.strip())
    except Exception:
        return None

manifest = {"built_at": time.time(), "files": []}

print("[INFO] MODE:", MODE)
if MODE == "info":
    print("[INFO] Building info video...")
    clip_length = 20
    styled_files = []
    for s in scenes:
        idx = s.get("idx")
        src = CLIPS / f"clip{idx}.mp4"
        print("[INFO] processing scene", idx, "src exists:", src.exists())
        if not src.exists():
            print("[WARN] Missing clip", src, " — skipping")
            continue
        trimmed = OUT / f"clip{idx}_trim.mp4"
        subprocess.run(["ffmpeg","-y","-ss","0","-i", str(src), "-t", str(clip_length),
                        "-vf", "scale=1280:720,setsar=1","-c:v","libx264","-preset","fast",
                        "-c:a","aac","-b:a","128k", str(trimmed)], check=True)
        caption = s.get("caption","").replace("'", r"\'").replace(":", r'\:')
        styled = OUT / f"clip{idx}_styled.mp4"
        drawtext = f"drawtext=text='{caption}':fontcolor=white:fontsize=36:box=1:boxcolor=0x00000099:boxborderw=10:x=(w-text_w)/2:y=h-120"
        subprocess.run(["ffmpeg","-y","-i", str(trimmed), "-vf", drawtext,
                        "-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(styled)], check=True)
        styled_files.append(styled)
    if not styled_files:
        print("[ERROR] No styled clips produced for info video.")
    else:
        listf = OUT / "info_list.txt"
        with open(listf, "w", encoding="utf-8") as f:
            for p in styled_files:
                f.write(f"file '{p.resolve()}'\n")
        final_tmp = OUT / f"final_{animal_key}_tmp.mp4"
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(final_tmp)], check=True)
        final_info = OUT / f"final_{animal_key}_info.mp4"
        narr = OUT / "narration.mp3"
        if narr.exists():
            vdur = get_duration(final_tmp) or 0
            adur = get_duration(narr) or 0
            tmp_audio = OUT / "narr_loop_tmp.mp3"
            if adur and adur < vdur:
                subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(narr), "-t", str(vdur), "-c","aac", str(tmp_audio)], check=True)
                audio_in = tmp_audio
            else:
                subprocess.run(["ffmpeg","-y","-ss","0","-i", str(narr), "-t", str(vdur), "-c","copy", str(tmp_audio)], check=True)
                audio_in = tmp_audio
            subprocess.run(["ffmpeg","-y","-i", str(final_tmp), "-i", str(audio_in), "-c:v","copy","-c:a","aac","-b:a","192k", str(final_info)], check=True)
            try: tmp_audio.unlink()
            except: pass
        else:
            shutil.move(str(final_tmp), str(final_info))
        print("[OK] Built info video:", final_info)
        manifest["files"].append(str(final_info.name))

elif MODE == "ambient":
    print("[INFO] Building ambient video...")
    available = sorted(CLIPS.glob("clip*.mp4"))
    if not available:
        print("[ERROR] No clips found for ambient build.")
    else:
        target_seconds = 7*60
        parts = []
        cur = 0
        i = 0
        while cur < target_seconds:
            src = available[i % len(available)]
            outseg = OUT / f"ambient_seg_{i}.mp4"
            seglen = min(60, target_seconds - cur)
            subprocess.run(["ffmpeg","-y","-ss","0","-i", str(src), "-t", str(seglen),
                            "-vf","scale=1280:720,setsar=1","-c:v","libx264","-preset","fast",
                            "-c:a","aac","-b:a","128k", str(outseg)], check=True)
            parts.append(outseg)
            cur += seglen
            i += 1
        listf = OUT / "ambient_list.txt"
        with open(listf, "w", encoding="utf-8") as f:
            for p in parts:
                f.write(f"file '{p.resolve()}'\n")
        tmp = OUT / f"ambient_{animal_key}_tmp.mp4"
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(tmp)], check=True)
        music_files = sorted(ASSETS_MUSIC.glob("*.mp3")) + sorted(ASSETS_MUSIC.glob("*.wav"))
        final = OUT / f"ambient_{animal_key}.mp4"
        if music_files:
            music = random.choice(music_files)
            vdur = get_duration(tmp) or 0
            if vdur and get_duration(music):
                music_tmp = OUT / "ambient_music_loop.mp3"
                adur = get_duration(music)
                if adur < vdur:
                    subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(music), "-t", str(vdur), "-c","aac", str(music_tmp)], check=True)
                else:
                    subprocess.run(["ffmpeg","-y","-ss","0","-i", str(music), "-t", str(vdur), "-c","copy", str(music_tmp)], check=True)
                subprocess.run(["ffmpeg","-y","-i", str(tmp), "-i", str(music_tmp), "-c:v","copy","-c:a","aac","-b:a","192k", str(final)], check=True)
                try: music_tmp.unlink()
                except: pass
            else:
                shutil.move(str(tmp), str(final))
        else:
            shutil.move(str(tmp), str(final))
        print("[OK] Built ambient video:", final)
        manifest["files"].append(str(final.name))

manifest_path = OUT / ".build_manifest.json"
open(manifest_path, "w", encoding="utf-8").write(json.dumps(manifest, indent=2))
print("[MANIFEST] Written:", manifest_path)
print("[OUTPUT FILES]")
for f in OUT.glob("*.mp4"):
    print(" -", f.name, f.stat().st_size)
