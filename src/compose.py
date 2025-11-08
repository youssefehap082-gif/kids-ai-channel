import os, tempfile, random
from pathlib import Path
from typing import List
from moviepy.editor import (
    VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, vfx
)
from pydub import AudioSegment
from PIL import Image

# إصلاح ANTIALIAS لمكتبة Pillow
if not hasattr(Image, "ANTIALIAS"):
    try:
        Image.ANTIALIAS = Image.Resampling.LANCZOS
    except Exception:
        pass

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
        mix = looped.overlay(narration)
        out = mix
    else:
        out = narration
    out_path = Path(tempfile.mkdtemp()) / "voicebed.mp3"
    out.export(out_path, format="mp3")
    return out_path

# =====================
#  INTRO & OUTRO CLIPS
# =====================

def make_intro(duration=4):
    txt = TextClip(
        "WildFacts Hub", fontsize=100, color="white", font="Arial-Bold", stroke_color="black", stroke_width=3
    ).set_position("center").set_duration(duration)
    sub = TextClip(
        "Discover Amazing Animal Facts!", fontsize=50, color="#FFD700", font="Arial-Bold"
    ).set_position(("center", 800)).set_duration(duration)
    bg = TextClip("", size=(1920, 1080), color=(0, 80, 0)).set_opacity(0.6).set_duration(duration)
    intro = CompositeVideoClip([bg, txt, sub]).fadein(0.5).fadeout(0.5)
    return intro

def make_outro(duration=6):
    main = TextClip(
        "Don't forget to subscribe and turn on the bell!", fontsize=70, color="white", font="Arial-Bold", stroke_color="black", stroke_width=3
    ).set_position("center").set_duration(duration)
    small = TextClip(
        "Thanks for watching!", fontsize=50, color="#FFD700", font="Arial-Bold"
    ).set_position(("center", 850)).set_duration(duration)
    bg = TextClip("", size=(1920, 1080), color=(20, 20, 20)).set_opacity(0.6).set_duration(duration)
    outro = CompositeVideoClip([bg, main, small]).fadein(0.5).fadeout(0.5)
    return outro

# =====================
#  COMPOSERS
# =====================

def compose_video(video_paths: List[Path], audio_path: Path, min_duration=185) -> Path:
    clips = []
    for p in video_paths:
        try:
            c = VideoFileClip(str(p)).fx(vfx.resize, height=1080)
            clips.append(c)
        except Exception as e:
            print(f"⚠️ Skipping invalid video: {e}")
    if not clips:
        raise Exception("❌ No valid videos to compose.")

    seq, cur, i = [], 0, 0
    while cur < min_duration and clips:
        c = clips[i % len(clips)]
        take = min(c.duration, max(5, min_duration - cur))
        seq.append(c.subclip(0, take))
        cur += take
        i += 1

    main_clip = concatenate_videoclips(seq, method="compose").set_audio(AudioFileClip(str(audio_path)))
    intro = make_intro()
    outro = make_outro()
    final = concatenate_videoclips([intro, main_clip, outro], method="compose")

    out_path = Path(tempfile.mkdtemp()) / "final_video.mp4"
    final.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="6000k")
    for c in clips: c.close()
    return out_path

def compose_short(video_paths: List[Path], audio_path: Path, target_duration=58) -> Path:
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
        take = min(c.duration, max(2, target_duration - cur))
        seq.append(c.subclip(0, take))
        cur += take
        if cur >= target_duration:
            break

    main_clip = concatenate_videoclips(seq, method="compose").set_audio(AudioFileClip(str(audio_path)))
    intro = make_intro(duration=3)
    outro = make_outro(duration=4)
    final = concatenate_videoclips([intro, main_clip, outro], method="compose")

    out_path = Path(tempfile.mkdtemp()) / "short.mp4"
    final.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="4000k")
    for c in clips: c.close()
    return out_path
