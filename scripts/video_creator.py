# scripts/video_creator.py
"""
Video assembly utilities (Production-ready).

Provides:
- assemble_long_video(clips_paths, voice_path, music_path=None, title_text=None, out_path=None, watermark=None)
- assemble_short_video(clip_path, music_path=None, out_path=None, vertical=False, watermark=None)

Features / Notes:
- Uses moviepy to open clips and compose them.
- Clips are trimmed to reasonable lengths per item to make ~3+ minute long videos.
- Adds voice audio (primary) and mixes optional background music at low volume.
- Adds a bottom textual CTA overlay if title_text provided.
- Adds a small watermark (text) at top-right.
- Writes final file (libx264 + aac) and returns Path to output file.
- Closes clips to free resources.
- Raises descriptive RuntimeError if moviepy not available or if composition fails.
"""

from pathlib import Path
import tempfile
import math
import logging
import shutil
import os

logger = logging.getLogger("video_creator")
logger.setLevel(logging.INFO)

TMP_DIR = Path(__file__).resolve().parent / "tmp"
TMP_DIR.mkdir(exist_ok=True, parents=True)


def _ensure_moviepy():
    try:
        import moviepy.editor as mpy
        return mpy
    except Exception as e:
        raise RuntimeError("moviepy not installed or failed to import. Ensure moviepy and imageio-ffmpeg are installed.") from e


def _close_clips(clips):
    for c in clips:
        try:
            c.close()
        except Exception:
            pass


def _mix_audio(voice_path, music_path, target_path, music_gain_db=-18):
    """
    Creates a mixed audio file where voice is primary and music is low-volume background.
    Returns path to mixed file.
    Uses moviepy audio or pydub if available.
    """
    try:
        # try moviepy audio mixing
        import moviepy.editor as mpy
        voice = mpy.AudioFileClip(str(voice_path))
        if music_path:
            music = mpy.AudioFileClip(str(music_path)).volumex(0.12)
            # combine so voice stays primary: set audio to voice, then overlay music where voice may be silent
            final_audio = mpy.CompositeAudioClip([music, voice.set_start(0)])
        else:
            final_audio = voice
        out = TMP_DIR / f"mixed_{int(math.floor(os.path.getmtime(str(voice_path))))}_{os.path.basename(str(voice_path))}"
        out = out.with_suffix(".mp3")
        # write using moviepy - ensure codec aac/ffmpeg handles mp3 output
        final_audio.write_audiofile(str(out), verbose=False, logger=None)
        try:
            voice.close()
        except:
            pass
        try:
            if music_path:
                music.close()
        except:
            pass
        return out
    except Exception as e:
        # fallback: if moviepy audio fails, simply return voice_path (no mixing)
        logger.warning("Audio mixing via moviepy failed, falling back to voice only: %s", e)
        return Path(voice_path)


def assemble_long_video(clips_paths,
                        voice_path,
                        music_path=None,
                        title_text=None,
                        out_path: str | Path = None,
                        watermark: str = None,
                        target_duration_sec: int = 180,
                        fps: int = 24):
    """
    Assemble multiple clips into one long video.
    - clips_paths: list of local clip paths (must exist)
    - voice_path: path to mp3 audio narration
    - music_path: optional background music mp3
    - title_text: optional small overlay call-to-action
    - out_path: optional destination path; if None -> TMP_DIR/final_long_{ts}.mp4
    - target_duration_sec: approximate final length target (controls subclip lengths)
    """
    mpy = _ensure_moviepy()

    if not clips_paths or len(clips_paths) == 0:
        raise RuntimeError("No clips provided for assemble_long_video")

    # open clips and trim each to a slice so total approx target_duration_sec
    clips = []
    opened = []
    try:
        total_available = 0.0
        for p in clips_paths:
            try:
                c = mpy.VideoFileClip(str(p))
                opened.append(c)
                total_available += getattr(c, "duration", 0) or 0
            except Exception as e:
                logger.warning("Failed to open clip %s: %s", p, e)

        if not opened:
            raise RuntimeError("Unable to open any clip files for long video assembly")

        # compute per-clip target slices so we reach target_duration_sec (but not exceed clip durations)
        per_clip_target = max(3, int(target_duration_sec / max(1, len(opened))))
        subclips = []
        for c in opened:
            dur = getattr(c, "duration", 0) or 0
            take = min(per_clip_target, int(dur))
            if take <= 0:
                # skip
                continue
            # pick a start time: prefer 10% into clip
            start = min(max(0.5, dur * 0.1), max(0.0, dur - take - 0.5))
            try:
                sc = c.subclip(start, start + take)
                subclips.append(sc)
            except Exception:
                try:
                    sc = c.subclip(0, take)
                    subclips.append(sc)
                except Exception:
                    continue

        if not subclips:
            raise RuntimeError("No valid subclips after trimming")

        final = mpy.concatenate_videoclips(subclips, method="compose")
        # set audio from voice (with optional music mixing)
        if voice_path:
            mixed_audio = _mix_audio(voice_path, music_path)
            audio_clip = mpy.AudioFileClip(str(mixed_audio))
            final = final.set_audio(audio_clip)
        elif music_path:
            audio_clip = mpy.AudioFileClip(str(music_path)).volumex(0.12)
            final = final.set_audio(audio_clip)

        # add watermark text (top-right) if requested
        if watermark:
            try:
                txt = mpy.TextClip(watermark, fontsize=24, color="white", stroke_color="black", stroke_width=2)
                txt = txt.set_duration(final.duration).set_pos(("right", "top")).margin(right=10, top=10)
                final = mpy.CompositeVideoClip([final, txt])
            except Exception as e:
                logger.warning("Failed to add watermark: %s", e)

        # add CTA title_text at end as 4-second overlay
        if title_text:
            try:
                txt = mpy.TextClip(title_text, fontsize=42, color="white", bg_color="black", size=final.size)
                txt = txt.set_duration(4).set_pos(("center", "bottom"))
                final = mpy.concatenate_videoclips([final, txt.set_audio(None)])
            except Exception as e:
                logger.warning("Failed to add end title overlay: %s", e)

        # output path
        if out_path is None:
            out_path = TMP_DIR / f"final_long_{int(mpy.time.time())}.mp4"
        else:
            out_path = Path(out_path)

        # ensure fps and codecs
        final.write_videofile(str(out_path), fps=fps, codec="libx264", audio_codec="aac", threads=2, verbose=False, logger=None)
        logger.info("Wrote long video: %s", out_path)
        return Path(out_path)
    finally:
        _close_clips(opened)
        try:
            # attempt to cleanup subclips if any
            for c in locals().get("subclips", []) or []:
                try:
                    c.close()
                except:
                    pass
        except:
            pass


def assemble_short_video(clip_path,
                         music_path=None,
                         out_path: str | Path = None,
                         vertical: bool = False,
                         watermark: str = None,
                         max_seconds: int = 20,
                         fps: int = 24):
    """
    Assemble a single short clip (for YouTube Shorts).
    - clip_path: single clip path (local)
    - music_path: optional background music
    - vertical: if True, produce vertical 9:16 (1080x1920) by cropping/letterboxing
    - out_path: destination path
    - max_seconds: cap clip length
    """
    mpy = _ensure_moviepy()

    try:
        clip = mpy.VideoFileClip(str(clip_path))
    except Exception as e:
        raise RuntimeError(f"Failed to open short clip {clip_path}: {e}")

    try:
        dur = getattr(clip, "duration", 0) or 0
        take = min(max_seconds, int(dur))
        if take <= 0:
            raise RuntimeError("Short clip has zero duration")

        short_clip = clip.subclip(0, take)

        # if vertical requested, crop/resize center to 9:16 (1080x1920)
        if vertical:
            target_w, target_h = (1080, 1920)
            # resize preserving aspect then crop center
            short_clip = short_clip.resize(height=target_h)
            # crop centered horizontally
            if short_clip.w > target_w:
                x_center = short_clip.w / 2
                x1 = max(0, int(x_center - target_w/2))
                short_clip = short_clip.crop(x1=x1, width=target_w)
            short_clip = short_clip.set_position(("center", "center"))
        else:
            # ensure standard width 1280 or keep original
            target_w, target_h = (1280, int(1280 * short_clip.h/short_clip.w)) if short_clip.w > 1280 else (int(short_clip.w), int(short_clip.h))
            short_clip = short_clip.resize(width=target_w)

        # add music background (no voice)
        if music_path:
            try:
                music = mpy.AudioFileClip(str(music_path)).volumex(0.18)
                short_clip = short_clip.set_audio(music)
            except Exception as e:
                logger.warning("Failed to attach music to short: %s", e)

        # watermark
        if watermark:
            try:
                txt = mpy.TextClip(watermark, fontsize=20, color="white", stroke_color="black", stroke_width=2)
                txt = txt.set_duration(short_clip.duration).set_pos(("right", "top")).margin(right=6, top=6)
                short_clip = mpy.CompositeVideoClip([short_clip, txt])
            except Exception as e:
                logger.warning("Short watermark failed: %s", e)

        if out_path is None:
            out_path = TMP_DIR / f"final_short_{int(mpy.time.time())}.mp4"
        else:
            out_path = Path(out_path)

        short_clip.write_videofile(str(out_path), fps=fps, codec="libx264", audio_codec="aac", threads=2, verbose=False, logger=None)
        logger.info("Wrote short video: %s", out_path)
        return Path(out_path)
    finally:
        try:
            clip.close()
        except:
            pass
        try:
            short_clip.close()
        except:
            pass
