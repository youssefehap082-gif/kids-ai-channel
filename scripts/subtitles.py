# scripts/subtitles.py
"""
Subtitles utilities:
- write_srt_from_transcript(transcript, out_path, wpm=150)
- write_vtt_from_transcript(transcript, out_path, wpm=150)
- burn_subtitles_on_video(video_path, srt_path, out_path)  # optional (uses moviepy.TextClip)
"""

from pathlib import Path
import math
import re
import logging
from typing import List, Tuple

logger = logging.getLogger("subtitles")
logger.setLevel(logging.INFO)


# --------------------
# Helpers: time formatting
# --------------------
def _seconds_to_timestamp(seconds: float) -> str:
    """
    Convert seconds (float) to SRT timestamp 'HH:MM:SS,mmm'
    """
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    s = total % 60
    total //= 60
    m = total % 60
    h = total // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _seconds_to_vtt_timestamp(seconds: float) -> str:
    """
    Convert seconds to VTT timestamp 'HH:MM:SS.mmm' (dot separator)
    """
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    s = total % 60
    total //= 60
    m = total % 60
    h = total // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


# --------------------
# Split transcript into lines of moderate length
# --------------------
def _split_into_lines(transcript: str, max_chars: int = 60) -> List[str]:
    """
    Break transcript into readable subtitle lines (no more than max_chars where possible).
    Keeps sentence boundaries when possible.
    """
    if not transcript:
        return []

    # Normalize whitespace
    t = re.sub(r"\s+", " ", transcript.strip())

    # First split by sentence punctuation to keep natural breaks
    sentences = re.split(r'(?<=[\.\?\!])\s+', t)
    lines = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(s) <= max_chars:
            lines.append(s)
        else:
            # break long sentence into chunks by words
            words = s.split()
            cur = []
            cur_len = 0
            for w in words:
                if cur_len + len(w) + 1 <= max_chars:
                    cur.append(w)
                    cur_len += len(w) + 1
                else:
                    lines.append(" ".join(cur))
                    cur = [w]
                    cur_len = len(w) + 1
            if cur:
                lines.append(" ".join(cur))
    # final cleanup
    lines = [ln.strip() for ln in lines if ln.strip()]
    return lines


# --------------------
# Duration allocation
# --------------------
def _estimate_durations(lines: List[str], wpm: int = 150, min_dur: float = 1.0) -> List[float]:
    """
    Estimate duration (seconds) for each subtitle line based on words-per-minute.
    Ensures each line has at least min_dur seconds.
    """
    durations = []
    for ln in lines:
        words = len(ln.split())
        # words per second = wpm / 60
        seconds = max(min_dur, (words / (wpm / 60.0)))
        durations.append(seconds)
    return durations


# --------------------
# SRT writer
# --------------------
def write_srt_from_transcript(transcript: str, out_path: str | Path, wpm: int = 150):
    """
    Convert transcript text to SRT file. Returns Path to SRT.
    """
    out = Path(out_path)
    lines = _split_into_lines(transcript)
    if not lines:
        # write an empty small srt with a default filler
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("1\n00:00:00,000 --> 00:00:02,000\nThis video contains information about the animal.\n")
        return out

    durations = _estimate_durations(lines, wpm=wpm)
    # build SRT entries
    cursor = 0.0
    srt_lines = []
    for idx, (ln, dur) in enumerate(zip(lines, durations), start=1):
        start = cursor
        end = cursor + dur
        srt_lines.append(str(idx))
        srt_lines.append(f"{_seconds_to_timestamp(start)} --> {_seconds_to_timestamp(end)}")
        srt_lines.append(ln)
        srt_lines.append("")  # blank line
        cursor = end

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(srt_lines), encoding="utf-8")
    logger.info("Wrote SRT: %s (%d entries)", out, len(lines))
    return out


# --------------------
# VTT writer
# --------------------
def write_vtt_from_transcript(transcript: str, out_path: str | Path, wpm: int = 150):
    """
    Create a WebVTT file suitable for YouTube or web players.
    """
    out = Path(out_path)
    lines = _split_into_lines(transcript)
    if not lines:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("WEBVTT\n\n00:00.000 --> 00:02.000\nThis video contains information about the animal.\n")
        return out

    durations = _estimate_durations(lines, wpm=wpm)
    cursor = 0.0
    vtt_lines = ["WEBVTT\n"]
    for ln, dur in zip(lines, durations):
        start = cursor
        end = cursor + dur
        vtt_lines.append(f"{_seconds_to_vtt_timestamp(start)} --> {_seconds_to_vtt_timestamp(end)}")
        vtt_lines.append(ln)
        vtt_lines.append("")
        cursor = end

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(vtt_lines), encoding="utf-8")
    logger.info("Wrote VTT: %s (%d entries)", out, len(lines))
    return out


# --------------------
# Burn subtitles on video (optional)
# --------------------
def burn_subtitles_on_video(video_path: str | Path, srt_path: str | Path, out_path: str | Path, font_size: int = 40):
    """
    Burn subtitles into video using moviepy.TextClip overlays.
    This is optional and may be slower; recommended for creating permanent burned captions.
    """
    try:
        from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    except Exception as e:
        logger.error("moviepy not available; cannot burn subtitles: %s", e)
        raise

    video_path = Path(video_path)
    srt_path = Path(srt_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # parse srt into (start,end,text) entries
    raw = srt_path.read_text(encoding="utf-8")
    entries = []
    parts = re.split(r"\n\s*\n", raw.strip())
    for p in parts:
        lines = p.strip().splitlines()
        if len(lines) >= 3:
            # first line is index, second is timing
            timing = lines[1].strip()
            m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", timing)
            if not m:
                continue
            def _to_sec(ts: str) -> float:
                h, m_, s_ms = ts.split(":")
                s, ms = s_ms.split(",")
                return int(h)*3600 + int(m_)*60 + int(s) + int(ms)/1000.0
            start = _to_sec(m.group(1))
            end = _to_sec(m.group(2))
            text = " ".join(lines[2:])
            entries.append((start, end, text))

    clip = VideoFileClip(str(video_path))
    subtitle_clips = []
    for (start, end, text) in entries:
        txt_clip = TextClip(text, fontsize=font_size, color="white", stroke_color="black", stroke_width=2, method="label")
        txt_clip = txt_clip.set_start(start).set_end(end).set_pos(("center", "bottom"))
        subtitle_clips.append(txt_clip)

    final = CompositeVideoClip([clip, *subtitle_clips])
    final.write_videofile(str(out_path), codec="libx264", audio_codec="aac")
    clip.close()
    for c in subtitle_clips:
        try:
            c.close()
        except:
            pass

    logger.info("Burned subtitles into video: %s", out_path)
    return out_path


# --------------------
# If run as script (quick test)
# --------------------
if __name__ == "__main__":
    sample = "This is a test transcript. It contains multiple sentences. Each sentence will be split into readable subtitle lines, with automatic timing computed from words-per-minute."
    write_srt_from_transcript(sample, Path("data/test.srt"))
    write_vtt_from_transcript(sample, Path("data/test.vtt"))
