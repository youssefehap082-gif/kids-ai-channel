import os, tempfile, random
from pathlib import Path
from typing import List
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, ImageClip, vfx
from PIL import Image, ImageDraw, ImageFont
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
        mix = looped.overlay(narration)
        out = mix
    else:
        out = narration
    out_path = Path(tempfile.mkdtemp()) / "voicebed.mp3"
    out.export(out_path, format="mp3")
    return out_path

# ------------------ Text Helpers ------------------

def _get_text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont):
    """Return width,height for text using either textbbox (new Pillow) or textsize (old Pillow)."""
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        return w, h
    else:
        return draw.textsize(text, font=font)

def make_text_image(text_top, text_bottom=None, bg_color=(10, 40, 10), size=(1920, 1080)):
    img = Image.new("RGB", size, color=bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("arial.ttf", 100)
        font_small = ImageFont.truetype("arial.ttf", 60)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    W, H = size
    w1, h1 = _get_text_size(draw, text_top, font_big)
    draw.text(((W - w1) / 2, H / 2 - 100), text_top, fill="white", font=font_big)

    if text_bottom:
        w2, h2 = _get_text_size(draw, text_bottom, font_small)
        draw.text(((W - w2) / 2, H / 2 + 50), text_bottom, fill="gold", font=font_small)

    tmp = Path(tempfile.mkdtemp()) / "text_image.jpg"
    img.save(tmp)
    return tmp

def make_intro(duration=4):
    path = make_text_image("WildFacts Hub", "Discover Amazing Animal Facts!")
    return ImageClip(str(path)).set_duration(duration).fadein(0.5).fadeout(0.5)

def make_outro(duration=6):
    path = make_text_image("Subscribe & Turn On The Bell!", "Thanks for watching!")
    return ImageClip(str(path)).set_duration(duration).fadein(0.5).fadeout(0.5)

# ------------------ Composers ------------------

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
        if cur >= target_duration: break

    main_clip = concatenate_videoclips(seq, method="compose").set_audio(AudioFileClip(str(audio_path)))
    intro = make_intro(duration=3)
    outro = make_outro(duration=4)
    final = concatenate_videoclips([intro, main_clip, outro], method="compose")

    out_path = Path(tempfile.mkdtemp()) / "short.mp4"
    final.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="4000k")
    for c in clips: c.close()
    return out_path
