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


# ======================================================
#  Create Title Image (NO IMAGEMAGICK, 100% SAFE)
# ======================================================
def make_title_image(text, width=1920, height=120, fontsize=48):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 180))
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default()

    # Safe textsize alternative
    bb = draw.textbbox((0, 0), text, font=font)
    w = bb[2] - bb[0]
    h = bb[3] - bb[1]

    draw.text(((width - w) / 2, (height - h) / 2), text, font=font, fill="white")

    out = TMP / "title.png"
    img.save(out)
    return str(out)


# ======================================================
#  Create Watermark bottom-right
# ======================================================
def add_watermark(clip, watermark_path, opacity=0.75):
    if not watermark_path or not os.path.exists(watermark_path):
        return clip

    wm = ImageClip(watermark_path).set_duration(clip.duration).resize(height=70)
    wm = wm.set_opacity(opacity)
    wm = wm.set_pos(("right", "bottom"))

    return CompositeVideoClip([clip, wm])


# ======================================================
#  Assemble LONG video (3 minutes)
# ======================================================
def assemble_long_video(clips, voice_path, music_path, title_text, watermark_path=None):
    if not clips:
        raise RuntimeError("No clips received for long video")

    processed = []

    for p in clips:
        try:
            v = VideoFileClip(p)
            sub = v.subclip(0, min(v.duration, 12))
            processed.append(sub)
        except:
            continue

    if not processed:
        raise RuntimeError("All long video clips failed to load")

    base = concatenate_videoclips(processed, method="compose")

    # Title
    title_img = make_title_image(title_text)
    title_clip = ImageClip(title_img).set_duration(4)
    final = concatenate_videoclips([title_clip, base], method="compose")

    # Voice
    if voice_path:
        voice = AudioFileClip(voice_path)
        final = final.set_audio(voice)

    # Music under voice
    if music_path:
        try:
            music = AudioFileClip(music_path).volumex(0.18)
            final = final.set_audio(final.audio.set_duration(final.duration))
        except:
            pass

    # Watermark
    if watermark_path:
        final = add_watermark(final, watermark_path)

    out = TMP / "long_final.mp4"
    final.write_videofile(
        str(out),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )
    return str(out)


# ======================================================
#  Assemble SHORT (voice 15s, video continues to 60s)
# ======================================================
def assemble_short(clip_path, music_path, voice_path=None, watermark_path=None):
    v = VideoFileClip(clip_path)

    voice_dur = 15
    total_dur = 60

    short = v.subclip(0, min(v.duration, total_dur))

    # Voice
    if voice_path:
        try:
            voice = AudioFileClip(voice_path)
            short = short.set_audio(voice)
        except:
            pass

    # Music
    if music_path:
        try:
            music = AudioFileClip(music_path).volumex(0.25)
            short = short.set_audio(short.audio if voice_path else music)
        except:
            pass

    # Watermark
    if watermark_path:
        short = add_watermark(short, watermark_path)

    out = TMP / "short_final.mp4"
    short.write_videofile(
        str(out),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )

    return str(out)
