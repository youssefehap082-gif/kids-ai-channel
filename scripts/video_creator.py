from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip
import os

TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)

def make_title_image(text, width, height=120, fontsize=48):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 200))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except:
        font = ImageFont.load_default()

    # FIX: textbbox بدل textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (width - text_w) // 2
    y = (height - text_h) // 2

    draw.text((x, y), text, fill="white", font=font)
    out = TMP / "title.png"
    img.save(out)
    return str(out)

def assemble_long_video(clips_paths, voice_path, music_path=None, title_text=None, watermark_path=None):
    clips = []
    for p in clips_paths:
        try:
            v = VideoFileClip(str(p))
            clips.append(v.subclip(0, min(10, v.duration)))
        except:
            continue

    if not clips:
        raise RuntimeError("No valid clips found")

    final = concatenate_videoclips(clips, method="compose")

    # إضافة تعليق صوتي
    if voice_path:
        voice_audio = AudioFileClip(str(voice_path))
        final = final.set_audio(voice_audio)

    # إضافة موسيقى خفيفة
    if music_path:
        try:
            music = AudioFileClip(str(music_path)).volumex(0.15)
        except:
            music = None

    # إضافة عنوان أول 4 ثواني
    if title_text:
        title_img = make_title_image(title_text, final.size[0])
        title_clip = VideoFileClip(title_img).set_duration(4)
        final = concatenate_videoclips([title_clip, final])

    # إضافة Watermark
    if watermark_path:
        wm = VideoFileClip(watermark_path).resize(height=60).set_opacity(0.7)
        final = CompositeVideoClip([final, wm.set_position(("right", "bottom"))])

    # حفظ الفيديو النهائي
    out_path = TMP / "long_final.mp4"
    final.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    return out_path
