import os, tempfile, random
from pathlib import Path
from typing import List
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from PIL import Image

# Pillow compat
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

def _download(url: str, to: Path):
    import requests
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    to.write_bytes(r.content)

def _dl_many(urls: List[str]) -> List[Path]:
    tmp = Path(tempfile.mkdtemp())
    paths=[]
    for i,u in enumerate(urls):
        try:
            p = tmp/f"clip_{i}.mp4"
            _download(u,p)
            paths.append(p)
        except Exception as e:
            print(f"⚠️ Download failed: {e}")
    return paths

def compose_video(urls: List[str], narration_mp3: str, min_duration=180) -> str:
    audio = AudioFileClip(narration_mp3)
    audio_len = audio.duration
    target = max(min_duration, int(audio_len))

    vpaths = _dl_many(urls)
    clips=[]
    for p in vpaths:
        try:
            c = VideoFileClip(str(p)).fx(vfx.resize, height=1080)
            clips.append(c)
        except Exception as e:
            print(f"⚠️ Bad clip: {e}")

    if not clips:
        raise RuntimeError("No valid video clips downloaded.")

    seq, cur, i = [], 0, 0
    while cur < target and clips:
        c = clips[i % len(clips)]
        take = min(c.duration, max(5, target - cur))
        seq.append(c.subclip(0, take))
        cur += take
        i += 1

    main = concatenate_videoclips(seq, method="compose").set_audio(audio)
    final = main.subclip(0, min(audio_len, main.duration))
    out = Path(tempfile.mkdtemp())/"long_final.mp4"
    final.write_videofile(str(out), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="6000k")

    for c in clips: c.close()
    audio.close()
    return str(out)

def compose_short(urls: List[str], target_duration=58) -> str:
    # Optional: try to fetch music from Pixabay if available
    music_path = None
    try:
        import requests
        pix_key = os.getenv("PIXABAY_API_KEY","")
        if pix_key:
            r = requests.get(f"https://pixabay.com/api/audio/?key={pix_key}&q=beat", timeout=20)
            j = r.json()
            if j.get("hits"):
                mp3 = j["hits"][0].get("audio")
                if mp3:
                    music_path = str(Path(tempfile.mkdtemp())/"short_music.mp3")
                    m = requests.get(mp3, timeout=60)
                    Path(music_path).write_bytes(m.content)
    except Exception as e:
        print(f"⚠️ Music fetch failed: {e}")

    vpaths = _dl_many(urls)
    clips=[]
    for p in vpaths:
        try:
            c = VideoFileClip(str(p)).resize(height=1920)
            if c.w > 1080:
                x = int((c.w - 1080)/2)
                c = c.crop(x1=x, y1=0, x2=x+1080, y2=1920)
            clips.append(c)
        except Exception as e:
            print(f"⚠️ Bad short clip: {e}")

    if not clips:
        raise RuntimeError("No valid short clips downloaded.")

    seq, cur = [], 0
    for c in clips:
        take = min(c.duration, max(2, target_duration - cur))
        seq.append(c.subclip(0, take))
        cur += take
        if cur >= target_duration: break

    main = concatenate_videoclips(seq, method="compose")
    if music_path:
        main = main.set_audio(AudioFileClip(music_path))
    out = Path(tempfile.mkdtemp())/"short_final.mp4"
    main.subclip(0, min(target_duration, main.duration)).write_videofile(str(out), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="4000k")
    for c in clips: c.close()
    return str(out)
