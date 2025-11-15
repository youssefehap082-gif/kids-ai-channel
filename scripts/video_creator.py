# scripts/video_creator.py

import os
from pathlib import Path
import logging
from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
)
import random

log = logging.getLogger("video_creator")

TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)


# ----------------------------------------------------------
# ASSEMBLE LONG VIDEO (up to 10–12 clips + voice + music)
# ----------------------------------------------------------
def assemble_long_video(clips, voice_path, music_path=None, title_text=None):
    try:
        video_clips = []

        for path in clips:
            try:
                clip = VideoFileClip(str(path))
                clip = clip.subclip(0, min(10, clip.duration))
                video_clips.append(clip)
            except Exception as e:
                log.error(f"Bad clip skipped: {e}")

        if not video_clips:
            raise RuntimeError("No valid video clips found.")

        final = concatenate_videoclips(video_clips, method="compose")

        # Voice
        if voice_path:
            voice = AudioFileClip(str(voice_path))
            final = final.set_audio(voice)

        # Music (optional)
        if music_path:
            try:
                music = AudioFileClip(str(music_path)).volumex(0.15)
                final = final.audio.set_fps(44100)
            except Exception:
                log.warning("Failed to add music background.")

        # Title overlay
        if title_text:
            txt = TextClip(
                title_text,
                fontsize=42,
                color="white",
                bg_color="black",
                size=(final.w, 150),
            ).set_duration(4)
            txt = txt.set_pos(("center", "bottom"))
            final = CompositeVideoClip([final, txt])

        out = TMP / "long_final.mp4"
        final.write_videofile(
            str(out), fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None
        )
        return out

    except Exception as e:
        log.error(f"LONG VIDEO FAILED: {e}")
        raise


# ----------------------------------------------------------
# ASSEMBLE SHORT (20–25 sec max) — Music only
# ----------------------------------------------------------
def assemble_short_video(clip_path, music_path=None):
    try:
        base = VideoFileClip(str(clip_path))
        base = base.subclip(0, min(20, base.duration))

        # Music only
        if music_path:
            try:
                music = AudioFileClip(str(music_path)).volumex(0.25)
                base = base.set_audio(music)
            except:
                pass

        out = TMP / f"short_{random.randint(100000,999999)}.mp4"
        base.write_videofile(
            str(out),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None,
        )
        return out
    except Exception as e:
        log.error(f"SHORT VIDEO FAILED: {e}")
        raise
