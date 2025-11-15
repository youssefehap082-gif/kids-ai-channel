# scripts/video_creator.py
"""
Video assembly utilities using MoviePy + pydub as needed.

Functions:
- assemble_long_video(clips_paths, voice_path=None, music_path=None, title_text=None, out_path=None)
- assemble_short(clip_path, music_path=None, out_path=None)

Notes:
- Expects ffmpeg installed on the runner (we install it in the GH Actions workflow).
- Uses moviepy.editor for main operations.
- For mixing voice + music we use pydub to render a single mixed audio file,
  then set that audio track on the final video (simpler & more reliable cross-platform).
- Carefully handles invalid clips and raises descriptive errors.
"""
from pathlib import Path
import logging
import tempfile
import shutil
import os
from typing import List, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# lazy imports (MoviePy and pydub may not be present at import-time in tests)
def _import_moviepy():
    try:
        from moviepy.editor import (
            VideoFileClip,
            concatenate_videoclips,
            AudioFileClip,
            CompositeVideoClip,
            TextClip,
        )
        return VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip
    except Exception as e:
        logger.exception("moviepy import failed: %s", e)
        raise

def _import_pydub():
    try:
        from pydub import AudioSegment
        return AudioSegment
    except Exception as e:
        logger.exception("pydub import failed: %s", e)
        raise

BASE_DIR = Path(__file__).resolve().parent
TMP = BASE_DIR / "tmp"
TMP.mkdir(exist_ok=True)

def _safe_open_video(path: str):
    VideoFileClip, *_ = _import_moviepy()
    try:
        clip = VideoFileClip(str(path))
        return clip
    except Exception as e:
        logger.warning("Failed to open video file '%s': %s", path, e)
        return None

def _mix_audio(voice_path: Optional[Path], music_path: Optional[Path], out_path: Path, music_volume: float = 0.10):
    """
    Mix voice (primary) with optional music (background) using pydub.
    voice_path and music_path are Path or None. Produces out_path as mp3.
    """
    AudioSegment = _import_pydub()
    base = None

    if voice_path and Path(voice_path).exists():
        try:
            base = AudioSegment.from_file(str(voice_path))
        except Exception as e:
            logger.warning("Could not read voice audio %s: %s", voice_path, e)
            base = None

    if music_path and Path(music_path).exists():
        try:
            music = AudioSegment.from_file(str(music_path))
            # reduce music volume
            music = music - (20 * (1 - music_volume))  # rough attenuation
        except Exception as e:
            logger.warning("Could not read music audio %s: %s", music_path, e)
            music = None
    else:
        music = None

    if base is None and music is None:
        raise RuntimeError("No audio sources available to mix.")

    if base is None:
        # only music available: export music as final audio
        final = music
    elif music is None:
        final = base
    else:
        # pad shorter track
        if len(music) < len(base):
            music = music * (int(len(base) / max(1, len(music))) + 1)
        if len(base) < len(music):
            base = base + AudioSegment.silent(duration=len(music) - len(base))
        # mix: base (voice) on top of music
        final = music.overlay(base)

    # ensure export path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.export(str(out_path), format="mp3")
    return out_path

def assemble_long_video(
    clips_paths: List[str],
    voice_path: Optional[str] = None,
    music_path: Optional[str] = None,
    title_text: Optional[str] = None,
    out_path: Optional[str] = None,
) -> Path:
    """
    Assemble a long video from multiple clips (takes up to first 10s of each clip)
    and attaches voice and optional music. Returns Path to final mp4.
    """
    VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip = _import_moviepy()

    tmpdir = Path(tempfile.mkdtemp(prefix="video_create_"))
    try:
        clips = []
        for p in clips_paths or []:
            if not p:
                continue
            clip = _safe_open_video(p)
            if not clip:
                continue
            duration = getattr(clip, "duration", None) or 0
            take = min(10, duration) if duration > 0 else 3
            try:
                sub = clip.subclip(0, take)
                clips.append(sub)
            except Exception:
                try:
                    clips.append(clip)
                except Exception:
                    continue

        if not clips:
            raise RuntimeError("No valid clips to assemble for long video.")

        final_clip = concatenate_videoclips(clips, method="compose")

        # prepare audio: mix voice + music (pydub) then attach as audio track
        mixed_audio_path = None
        if voice_path or music_path:
            mixed_audio_path = tmpdir / "mixed_audio.mp3"
            try:
                _mix_audio(Path(voice_path) if voice_path else None, Path(music_path) if music_path else None, mixed_audio_path)
                audio_clip = AudioFileClip(str(mixed_audio_path))
                final_clip = final_clip.set_audio(audio_clip)
            except Exception as e:
                logger.warning("Audio mixing failed: %s", e)
                # if mixing fails, attempt to set voice alone
                if voice_path and Path(voice_path).exists():
                    try:
                        audio_clip = AudioFileClip(str(voice_path))
                        final_clip = final_clip.set_audio(audio_clip)
                    except Exception:
                        pass

        # add title overlay if given (brief)
        if title_text:
            try:
                txt = TextClip(title_text, fontsize=40, color="white", bg_color="black", size=final_clip.size)
                txt = txt.set_duration(min(4, final_clip.duration)).set_pos(("center", "bottom"))
                final_clip = CompositeVideoClip([final_clip, txt])
            except Exception as e:
                logger.warning("Title overlay failed: %s", e)

        # output
        if out_path is None:
            out_path = TMP / "final_long.mp4"
        else:
            out_path = Path(out_path)

        # ensure target folder
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # write file (moviepy will call ffmpeg)
        # use logger-friendly args
        final_clip.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac")

        # close clips to release handles
        final_clip.close()
        for c in clips:
            try:
                c.close()
            except Exception:
                pass

        return out_path

    finally:
        # cleanup tmpdir
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

def assemble_short(clip_path: Optional[str], music_path: Optional[str] = None, out_path: Optional[str] = None) -> Path:
    """
    Assemble a short video: takes up to 20s from clip_path and attaches music (no voice for shorts).
    If clip_path is None or invalid raises RuntimeError.
    """
    VideoFileClip, _, AudioFileClip, CompositeVideoClip, TextClip = _import_moviepy()

    if not clip_path:
        raise RuntimeError("No clip path provided for short.")

    clip = _safe_open_video(clip_path)
    if clip is None:
        raise RuntimeError(f"Could not open short clip: {clip_path}")

    duration = getattr(clip, "duration", None) or 0
    take = min(20, duration) if duration > 0 else min(20, 5)
    c = clip.subclip(0, take)

    if music_path:
        try:
            # set music audio
            music_audio = AudioFileClip(str(music_path))
            # If music longer than clip, set_audio will loop? MoviePy doesn't loop automatically,
            # so we trim music to clip duration
            music_trim = music_audio.subclip(0, min(music_audio.duration, c.duration))
            c = c.set_audio(music_trim)
        except Exception as e:
            logger.warning("Short music attach failed: %s", e)

    if out_path is None:
        out_path = TMP / "final_short.mp4"
    else:
        out_path = Path(out_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    c.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac")

    try:
        c.close()
    except Exception:
        pass

    return out_path
