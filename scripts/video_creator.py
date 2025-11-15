from moviepy.editor import (
    VideoFileClip, concatenate_videoclips, AudioFileClip,
    CompositeVideoClip, TextClip
)
from pathlib import Path
import os
import uuid

TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)

WATERMARK_TEXT = "WildFacts Hub"

def add_watermark(clip):
    wm = TextClip(
        WATERMARK_TEXT,
        fontsize=28,
        color="white",
        font="Arial-Bold",
        bg_color=None
    ).set_opacity(0.7)

    wm = wm.set_position(("right", "bottom")).set_duration(clip.duration)
    return CompositeVideoClip([clip, wm])


def add_subscribe_end(clip):
    txt = TextClip(
        "Don't forget to subscribe for more amazing animal facts!",
        fontsize=35,
        color="white",
        bg_color="black"
    ).set_duration(3).set_position(("center", "bottom"))
    return CompositeVideoClip([clip, txt])


def assemble_long_video(clips_paths, voice_path, music_path=None, out_path=None):
    clips = []
    for p in clips_paths:
        try:
            v = VideoFileClip(str(p))
            sub = v.subclip(0, min(10, v.duration))
            clips.append(sub)
        except:
            pass

    if not clips:
        raise RuntimeError("No valid clips for long video.")

    base = concatenate_videoclips(clips, method="compose")

    # audio
    voice = AudioFileClip(str(voice_path))
    final_audio = voice

    if music_path:
        try:
            music = AudioFileClip(str(music_path)).volumex(0.12)
            from moviepy.audio.AudioClip import CompositeAudioClip
            final_audio = CompositeAudioClip([voice, music])
        except:
            pass

    base = base.set_audio(final_audio)

    # length = 3 minutes
    target = 180
    if base.duration < target:
        loops = int(target / base.duration) + 1
        base = concatenate_videoclips([base] * loops).subclip(0, target)
    else:
        base = base.subclip(0, target)

    base = add_watermark(base)
    base = add_subscribe_end(base)

    if out_path is None:
        out_path = TMP / "long_final.mp4"

    base.write_videofile(
        str(out_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    return str(out_path)


def assemble_short(clips_paths, music_path=None, out_path=None, max_duration=60):
    clips = []
    total = 0

    for p in clips_paths:
        try:
            v = VideoFileClip(str(p))
            cut = v.subclip(0, min(5, v.duration))
            clips.append(cut)
            total += cut.duration
            if total >= max_duration:
                break
        except:
            pass

    if not clips:
        raise RuntimeError("No valid clips for short video.")

    base = concatenate_videoclips(clips, method="compose")
    base = base.subclip(0, min(max_duration, base.duration))

    if music_path:
        try:
            music = AudioFileClip(str(music_path)).volumex(0.15)
            base = base.set_audio(music)
        except:
            pass

    base = add_watermark(base)

    if out_path is None:
        out_path = TMP / f"short_{uuid.uuid4().hex}.mp4"

    base.write_videofile(
        str(out_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )
    return str(out_path)
