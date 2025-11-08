import os, tempfile, random
from pathlib import Path
from typing import List
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from PIL import Image
from pydub import AudioSegment

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

def download_files(urls: List[str], workdir: Path) -> List[Path]:
    import requests
    paths = []
    for i, u in enumerate(urls):
        try:
            r = requests.get(u, timeout=300)
            r.raise_for_status()
            p = workdir / f"clip_{i}.mp4"
            p.write_bytes(r.content)
            paths.append(p)
        except Exception as e:
            print(f"⚠️ Failed to download video: {e}")
    return paths

def pick_bg_music(music_dir: Path) -> Path | None:
    tracks = list(music_dir.glob("*.mp3"))
    return random.choice(tracks) if tracks else None

def make_voicebed(voice_paths: List[Path], bg_music: Path | None = None, music_gain_db=-18) -> Path:
    narration = AudioSegment.silent(duration=0)
    for p in voice_paths:
        narration += AudioSegment.from_file(p)
    if bg_music:
        music = AudioSegment.from_file(bg_music) - abs(music_gain_db)
        looped = (music * (int(len(narration) / len(music)) + 2))[:len(narration)]
        out = looped.overlay(narration)
    else:
        out = narration
    out_path = Path(tempfile.mkdtemp()) / "voicebed.mp3"
    out.export(out_path, format="mp3")
    return out_path

def compose_video(video_paths: List[Path], audio_path: Path, min_duration=185) -> Path:
    audio_clip = AudioFileClip(str(audio_path))
    audio_len = audio_clip.duration

    clips = []
    for p in video_paths:
        try:
            c = VideoFileClip(str(p)).fx(vfx.resize, height=1080)
            clips.append(c)
        except Exception as e:
            print(f"⚠️ Skipping invalid video: {e}")

    if not clips:
        raise Exception("❌ No valid videos to compose.")

    target = max(min_duration, int(audio_len))
    seq, cur, i = [], 0, 0
    while cur < target and clips:
        c = clips[i % len(clips)]
        take = min(c.duration, max(5, target - cur))
        seq.append(c.subclip(0, take))
        cur += take
        i += 1

    main = concatenate_videoclips(seq, method="compose").set_audio(audio_clip)
    final = main.subclip(0, min(audio_len, main.duration))  # <-- بدون أي زيادة

    out_path = Path(tempfile.mkdtemp()) / "final_video.mp4"
    final.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="6000k")

    for c in clips: c.close()
    audio_clip.close()
    return out_path

def compose_short(video_paths: List[Path], music_path: Path, target_duration=58) -> Path:
    music_clip = AudioFileClip(str(music_path))
    music_len = music_clip.duration
    target = min(target_duration, int(music_len))

    clips = []
    for p in video_paths:
        try:
            c = VideoFileClip(str(p)).resize(height=1920)
            if c.w > 1080:
                x = int((c.w - 1080) / 2)
                c = c.crop(x1=x, y1=0, x2=x+1080, y2=1920)
            clips.append(c)
        except Exception as e:
            print(f"⚠️ Skipping invalid short video: {e}")

    if not clips:
        raise Exception("❌ No valid videos for short.")

    seq, cur = [], 0
    for c in clips:
        take = min(c.duration, max(2, target - cur))
        seq.append(c.subclip(0, take))
        cur += take
        if cur >= target:
            break

    main = concatenate_videoclips(seq, method="compose").set_audio(music_clip)
    final = main.subclip(0, min(music_len, main.duration))

    out_path = Path(tempfile.mkdtemp()) / "short.mp4"
    final.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="4000k")

    for c in clips: c.close()
    music_clip.close()
    return out_path
