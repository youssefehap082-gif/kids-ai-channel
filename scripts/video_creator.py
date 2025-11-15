# scripts/video_creator.py
from moviepy.editor import (
    VideoFileClip, concatenate_videoclips, AudioFileClip,
    CompositeVideoClip, TextClip, afx
)
from pathlib import Path
import os
import logging

LOG = logging.getLogger(__name__)

TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

# watermark text (read from env so you can change easily)
WATERMARK_TEXT = os.getenv('WATERMARK_TEXT', '@WildPlanetFacts')
WATERMARK_FONTSIZE = int(os.getenv('WATERMARK_FONTSIZE', '22'))
WATERMARK_MARGIN = int(os.getenv('WATERMARK_MARGIN', '12'))  # pixels from corner


def _make_watermark_clip(size, duration=5):
    # create a small TextClip to use as watermark
    txt = TextClip(WATERMARK_TEXT, fontsize=WATERMARK_FONTSIZE, color='white', bg_color='rgba(0,0,0,0.35)')
    txt = txt.set_duration(duration)
    txt = txt.set_pos(('right', 'bottom'))
    # position offset by margin
    w, h = size
    txt = txt.margin(right=WATERMARK_MARGIN, bottom=WATERMARK_MARGIN)
    return txt


def assemble_long_video(clips_paths, voice_path, music_path=None, title_text=None, out_path=None):
    clips = []
    # load and cut each clip to up to 10s
    for p in clips_paths:
        try:
            v = VideoFileClip(str(p))
            sub = v.subclip(0, min(10, v.duration))
            clips.append(sub)
        except Exception as e:
            LOG.warning("Skipping clip %s: %s", p, e)
            continue

    if not clips:
        raise RuntimeError('No valid clips to assemble')

    final = concatenate_videoclips(clips, method='compose')

    # voice audio
    if voice_path and Path(voice_path).exists():
        try:
            voice_audio = AudioFileClip(str(voice_path))
            # Attach voice as main audio (if voice shorter than video, it will loop or be shorter)
            final = final.set_audio(voice_audio)
        except Exception as e:
            LOG.warning("Failed to attach voice audio: %s", e)

    # mix music softly if provided
    if music_path and Path(music_path).exists():
        try:
            music = AudioFileClip(str(music_path)).volumex(0.12)
            # if voice exists, overlay music under voice
            if final.audio:
                combined = afx.audio_loop(music, duration=final.duration).volumex(0.12)
                # set final audio to voice if exists; here moviepy mixing is manual: prefer voice
                final = final.set_audio(final.audio)  # keep voice audio
                # NOTE: moviepy mixing advanced usage omitted for simplicity
            else:
                final = final.set_audio(music)
        except Exception as e:
            LOG.warning("Failed to attach music: %s", e)

    # add title text at end (4s)
    if title_text:
        try:
            txt = TextClip(title_text, fontsize=40, color='white', bg_color='black', size=final.size)
            txt = txt.set_duration(4).set_pos(('center', 'bottom'))
            final = CompositeVideoClip([final, txt])
        except Exception as e:
            LOG.warning("Failed to add title text: %s", e)

    # watermark (use duration of final video)
    try:
        wm = _make_watermark_clip(final.size, duration=final.duration)
        final = CompositeVideoClip([final, wm])
    except Exception as e:
        LOG.warning("Failed to add watermark: %s", e)

    if out_path is None:
        out_path = TMP / 'final_long.mp4'
    # write file - disable verbose heavy logs to keep GH Actions readable
    final.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return Path(out_path)


def assemble_short(clip_path, music_path=None, out_path=None):
    # Fix: avoid calling VideoFileClip twice and handle exceptions
    clip_path = Path(clip_path)
    if not clip_path.exists():
        raise RuntimeError(f'Short clip not found: {clip_path}')

    try:
        v = VideoFileClip(str(clip_path))
        c = v.subclip(0, min(20, v.duration))
    except Exception as e:
        raise RuntimeError(f'Error opening short clip {clip_path}: {e}')

    # music overlay
    if music_path and Path(music_path).exists():
        try:
            music = AudioFileClip(str(music_path)).volumex(0.2)
            # loop music if shorter than clip
            if music.duration < c.duration:
                from moviepy.audio.fx.all import audio_loop
                music = audio_loop(music, duration=c.duration)
            c = c.set_audio(music)
        except Exception as e:
            LOG.warning("Failed to set music for short: %s", e)

    # watermark
    try:
        wm = _make_watermark_clip(c.size, duration=c.duration)
        final = CompositeVideoClip([c, wm])
    except Exception as e:
        LOG.warning("Failed to apply watermark on short: %s", e)
        final = c

    if out_path is None:
        out_path = TMP / 'final_short.mp4'
    final.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return Path(out_path)
