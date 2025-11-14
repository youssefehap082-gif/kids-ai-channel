# scripts/video_creator.py
"""
Assemble long videos and shorts from local clips, voice audio and music.
Uses vendored MoviePy modules placed under scripts/ (VideoClip.py, AudioClip.py, Clip.py, compositing/ etc.)
"""

from VideoClip import VideoFileClip
from AudioClip import AudioFileClip
from Clip import concatenate_videoclips
from compositing.CompositeVideoClip import CompositeVideoClip
from tools.subtitles import TextClip

from pathlib import Path
import os
import math

TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def _safe_open_video(path):
    try:
        clip = VideoFileClip(str(path))
        return clip
    except Exception as e:
        return None

def assemble_long_video(clips_paths, voice_path, music_path=None, title_text=None, out_path=None):
    """
    clips_paths: list of local video file paths
    voice_path: path to voice audio (mp3/wav) or None
    music_path: optional background music path
    title_text: optional text to overlay at the end
    out_path: optional output path (string or Path)
    """
    clips = []
    for p in clips_paths:
        try:
            v = _safe_open_video(p)
            if v is None:
                continue
            # take up to 10 seconds from each clip
            dur = min(10, getattr(v, "duration", 10) or 10)
            clips.append(v.subclip(0, dur))
        except Exception:
            continue

    if not clips:
        raise RuntimeError('No valid clips to assemble')

    final = concatenate_videoclips(clips, method='compose')

    # set primary audio: prefer voice_path; otherwise try music
    audio_set = False
    if voice_path:
        try:
            voice_audio = AudioFileClip(str(voice_path))
            final = final.set_audio(voice_audio)
            audio_set = True
        except Exception:
            audio_set = False

    if not audio_set and music_path:
        try:
            music = AudioFileClip(str(music_path))
            final = final.set_audio(music)
            audio_set = True
        except Exception:
            audio_set = False

    # If both voice and music exist and we want to keep voice primarily,
    # prefer voice (already set). If you later want mixing, implement CompositeAudioClip.
    # Add end CTA/title text overlay
    if title_text:
        try:
            # build a short TextClip and overlay at bottom for 4 seconds
            txtclip = TextClip(title_text, fontsize=40, color='white', bg_color='black', size=final.size, duration=4)
            txtclip = txtclip.set_pos(('center', 'bottom')).set_duration(4)
            # place the text at the end of the video
            final = final.set_duration(final.duration + 4)
            final = CompositeVideoClip([final, txtclip.set_start(final.duration - 4)])
        except Exception:
            # ignore text overlay failures
            pass

    if out_path is None:
        out_path = TMP / 'final_long.mp4'
    out_path = Path(out_path)

    # Export final video
    final.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')

    # close clips to free resources (if vendor clips implement close)
    try:
        for c in clips:
            if hasattr(c, "close"):
                c.close()
    except Exception:
        pass

    return str(out_path)


def assemble_short(clip_path, music_path=None, out_path=None):
    """
    Create a short (vertical or square) from a single clip_path and optional music.
    Ensures we don't open the clip twice and we handle duration safely.
    """
    clip = _safe_open_video(clip_path)
    if clip is None:
        raise RuntimeError("Invalid short clip")

    try:
        duration = min(20, getattr(clip, "duration", 20) or 20)
        c = clip.subclip(0, duration)
    except Exception:
        c = clip

    if music_path:
        try:
            music = AudioFileClip(str(music_path))
            c = c.set_audio(music)
        except Exception:
            # ignore audio set failures
            pass

    if out_path is None:
        out_path = TMP / 'final_short.mp4'
    out_path = Path(out_path)

    c.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')

    try:
        if hasattr(clip, "close"):
            clip.close()
    except Exception:
        pass

    return str(out_path)
