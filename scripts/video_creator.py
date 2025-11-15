import os
from pathlib import Path
from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    AudioFileClip,
    CompositeVideoClip,
    ImageClip
)
from PIL import Image, ImageDraw, ImageFont
import tempfile

TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)

def make_title_image(text, width=1920, height=120, fontsize=48):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 180))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", fontsize)
    except:
        font = ImageFont.load_default()
    bb = draw.textbbox((0, 0), text, font=font)
    w = bb[2] - bb[0]
    h = bb[3] - bb[1]
    draw.text(((width - w) / 2, (height - h) / 2), text, font=font, fill="white")
    out = TMP / f"title_{abs(hash(text))%100000}.png"
    img.save(out)
    return str(out)

def add_watermark(clip, watermark_path, opacity=0.3):
    if not watermark_path or not os.path.exists(watermark_path):
        return clip
    wm = ImageClip(watermark_path).set_duration(clip.duration).resize(height=70).set_opacity(opacity).set_pos(("right","bottom"))
    return CompositeVideoClip([clip, wm])

def assemble_long_video(clips, voice_path=None, music_path=None, title_text=None, watermark_path=None, target_duration=180):
    if not clips:
        raise RuntimeError("No clips received for long video")
    processed = []
    total = 0.0
    for p in clips:
        try:
            v = VideoFileClip(str(p))
            length = min(15, v.duration)
            processed.append(v.subclip(0, length))
            total += length
            if total >= target_duration:
                break
        except Exception:
            continue
    if not processed:
        raise RuntimeError("All long video clips failed to load")
    base = concatenate_videoclips(processed, method="compose")
    # Title overlay first 4s
    if title_text:
        title_img = make_title_image(title_text, width=base.size[0])
        title_clip = ImageClip(title_img).set_duration(4).set_pos(("center","top"))
        base = CompositeVideoClip([base, title_clip.set_start(0)])
    # Set audio: prefer voice_path
    if voice_path and os.path.exists(voice_path):
        try:
            voice = AudioFileClip(str(voice_path))
            base = base.set_audio(voice.set_duration(base.duration))
        except Exception:
            pass
    elif music_path and os.path.exists(music_path):
        try:
            music = AudioFileClip(str(music_path)).volumex(0.12)
            base = base.set_audio(music.set_duration(base.duration))
        except Exception:
            pass
    # watermark
    if watermark_path:
        base = add_watermark(base, watermark_path, opacity=0.3)
    out = TMP / "long_final.mp4"
    base.write_videofile(str(out), fps=24, codec="libx264", audio_codec="aac")
    return str(out)

def assemble_short(clip_path, music_path=None, voice_path=None, watermark_path=None, voice_duration=15, max_duration=60):
    try:
        v = VideoFileClip(str(clip_path))
    except Exception as e:
        raise RuntimeError("Short clip open failed: " + str(e))
    # prepare visual
    clips = []
    total = 0.0
    i = 0
    while total < max_duration and i < 10:
        length = min(5, v.duration)
        clips.append(v.subclip(0, length))
        total += length
        i += 1
    base = concatenate_videoclips(clips, method="compose")
    # voice primary segment
    if voice_path and os.path.exists(voice_path):
        try:
            voice = AudioFileClip(str(voice_path)).subclip(0, min(voice_duration, AudioFileClip(voice_path).duration))
            # ensure base length at least voice length
            if base.duration < voice.duration:
                loops = int(voice.duration // base.duration) + 1
                base = concatenate_videoclips([base] * loops).subclip(0, voice.duration)
            base = base.set_audio(voice.set_duration(base.duration))
        except Exception:
            pass
    else:
        if music_path and os.path.exists(music_path):
            try:
                music = AudioFileClip(str(music_path)).subclip(0, min(max_duration, base.duration)).volumex(0.15)
                base = base.set_audio(music.set_duration(base.duration))
            except Exception:
                pass
    # watermark
    if watermark_path:
        base = add_watermark(base, watermark_path, opacity=0.3)
    base = base.subclip(0, min(max_duration, base.duration))
    out = TMP / "short_final.mp4"
    base.write_videofile(str(out), fps=24, codec="libx264", audio_codec="aac")
    return str(out)
