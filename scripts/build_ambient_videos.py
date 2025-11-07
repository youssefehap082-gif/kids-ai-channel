#!/usr/bin/env python3
# scripts/build_ambient_videos.py
# Build ambient videos ~5-7 minutes using clips and music (assets/music/)
import os, json, random, subprocess, time
from pathlib import Path
OUT = Path("output")
CLIPS = Path("clips")
MUSIC = Path("assets/music")
OUT.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)
MUSIC.mkdir(parents=True, exist_ok=True)

def safe_duration(path):
    try:
        import subprocess
        out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(path)])
        return float(out.strip())
    except:
        return None

def build_ambient(name_suffix, minutes=6):
    target = int(minutes*60)
    available = sorted(CLIPS.glob("*.mp4"))
    if not available:
        print("No clips available - will create simple color ambient")
        outv = OUT / f"ambient_fallback_{name_suffix}.mp4"
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x001122:s=1280x720:d={target}","-c:v","libx264","-pix_fmt","yuv420p", str(outv)], check=True)
        return outv
    parts = []
    cur = 0
    i = 0
    while cur < target:
        src = available[i % len(available)]
        seg_len = min(30, target - cur)
        seg = OUT / f"amb_seg_{name_suffix}_{i}.mp4"
        subprocess.run(["ffmpeg","-y","-ss","0","-i", str(src), "-t", str(seg_len), "-vf","scale=1280:720,setsar=1","-c:v","libx264","-preset","fast","-c:a","aac","-b:a","128k", str(seg)], check=True)
        parts.append(seg)
        cur += seg_len
        i += 1
    listf = OUT / f"amb_list_{name_suffix}.txt"
    with open(listf,"w",encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.resolve()}'\n")
    tmp = OUT / f"ambient_{name_suffix}_tmp.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i", str(listf), "-c","copy", str(tmp)], check=True)
    # attach music if exists
    mus = list(MUSIC.glob("*.mp3")) + list(MUSIC.glob("*.wav"))
    final = OUT / f"ambient_{name_suffix}.mp4"
    if mus:
        music = random.choice(mus)
        vdur = safe_duration(tmp) or 0
        tmp_music = OUT / f"amb_music_{name_suffix}.mp3"
        if vdur>0:
            adur = safe_duration(music) or 0
            if adur>0 and adur < vdur:
                subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", str(music), "-t", str(vdur), "-c","aac", str(tmp_music)], check=True)
            else:
                subprocess.run(["ffmpeg","-y","-ss","0","-i", str(music), "-t", str(vdur), "-c","copy", str(tmp_music)], check=True)
            subprocess.run(["ffmpeg","-y","-i", str(tmp), "-i", str(tmp_music), "-c:v","copy","-c:a","aac","-b:a","192k", str(final)], check=True)
            try: tmp_music.unlink()
            except: pass
        else:
            subprocess.run(["ffmpeg","-y","-i", str(tmp), "-c","copy", str(final)], check=True)
    else:
        subprocess.run(["ffmpeg","-y","-i", str(tmp), "-c","copy", str(final)], check=True)
    # clean parts
    for p in parts:
        try: p.unlink()
        except: pass
    try:
        listf.unlink()
        tmp.unlink()
    except: pass
    print("Built ambient:", final.name)
    return final

if __name__ == "__main__":
    a1 = build_ambient("1", minutes=6.5)
    a2 = build_ambient("2", minutes=5.5)
    manifest = {"files":[a1.name if a1 else None, a2.name if a2 else None]}
    open(OUT / ".build_manifest_ambient.json","w",encoding="utf-8").write(json.dumps(manifest, indent=2))
