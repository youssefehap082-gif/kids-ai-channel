from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip, ImageClip
from pathlib import Path
import tempfile, os

TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def assemble_long_video(clips_paths, voice_path=None, music_path=None, title_text=None, watermark_path=None, out_path=None, target_duration=180):
    """
    Create a long video (~3 minutes default).
    - clips_paths: list of video file paths (will be concatenated)
    - voice_path: audio narration file (optional) — if present, set as main audio
    - music_path: background music (optional) — mixed under voice
    - title_text: optional title overlay (few seconds at start)
    - watermark_path: optional small PNG to overlay bottom-left or right
    - target_duration: final target duration seconds (trim/pad as appropriate)
    """
    clips = []
    total = 0.0
    for p in clips_paths:
        try:
            v = VideoFileClip(str(p))
            # take full clip or a limited slice, but keep reasonable
            length = min(v.duration, 15)  # use up to 15s per clip to make variety
            clips.append(v.subclip(0, length))
            total += length
            if total >= target_duration:
                break
        except Exception as e:
            # skip invalid clip
            continue

    if not clips:
        raise RuntimeError('No valid clips to assemble')

    final = concatenate_videoclips(clips, method='compose')

    # set audio: voice_primary + optional music mixed under it
    if voice_path and Path(voice_path).exists():
        voice_audio = AudioFileClip(str(voice_path))
        # if voice longer/shorter than final, use either loop or cut
        final = final.set_audio(voice_audio.set_duration(final.duration))
    if music_path and Path(music_path).exists():
        try:
            music = AudioFileClip(str(music_path)).volumex(0.10)
            # If we already set voice, we want voice primary; mixing here is complex.
            # A simple approach: if voice exists, overlay music by setting final audio to voice, and mix externally if needed.
            # moviepy doesn't provide easy 'mix' in this simple script — keep music only if no voice.
            if not voice_path:
                final = final.set_audio(music.set_duration(final.duration))
        except Exception:
            pass

    # Title overlay for first few seconds
    if title_text:
        txt = TextClip(title_text, fontsize=48, color='white', bg_color='black', size=final.size)
        txt = txt.set_duration(4).set_pos(('center','bottom'))
        final = CompositeVideoClip([final, txt])

    # watermark (small transparent PNG) bottom-right by default
    if watermark_path and Path(watermark_path).exists():
        try:
            wm = (ImageClip(str(watermark_path))
                  .set_duration(final.duration)
                  .resize(height=60)  # small watermark
                  .margin(right=8, bottom=8, opacity=0)
                  .set_pos(("right", "bottom")))
            final = CompositeVideoClip([final, wm])
        except Exception:
            pass

    if out_path is None:
        out_path = TMP / 'final_long.mp4'
    final.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return str(out_path)

def assemble_short(clip_path, voice_path=None, music_path=None, watermark_path=None, out_path=None, max_duration=60):
    """
    Create a short video (target 15-60s). 
    - clip_path: single clip or a short video path
    - voice_path: optional narration (can be 10-20s)
    - music_path: background music
    - If voice given, keep voice as primary audio and extend clip to match voice duration if possible.
    """
    if not Path(clip_path).exists():
        raise RuntimeError(f'Clip not found: {clip_path}')

    vc = VideoFileClip(str(clip_path))
    duration = min(max_duration, vc.duration)
    # if we have voice and it's shorter or longer, we'll trim/pad
    final_clip = vc.subclip(0, duration)

    # set audio: voice if present, otherwise music
    if voice_path and Path(voice_path).exists():
        voice_audio = AudioFileClip(str(voice_path))
        # ensure final clip has same duration as voice (trim or loop the clip)
        vdur = voice_audio.duration
        if final_clip.duration >= vdur:
            final_clip = final_clip.subclip(0, vdur)
        else:
            # loop the visual to match voice duration
            loops = int(vdur // final_clip.duration) + 1
            final_clip = concatenate_videoclips([final_clip] * loops)
            final_clip = final_clip.subclip(0, vdur)
        final_clip = final_clip.set_audio(voice_audio.set_duration(final_clip.duration))
    elif music_path and Path(music_path).exists():
        try:
            music = AudioFileClip(str(music_path)).volumex(0.20)
            final_clip = final_clip.set_audio(music.set_duration(final_clip.duration))
        except Exception:
            pass

    # watermark
    if watermark_path and Path(watermark_path).exists():
        try:
            wm = (ImageClip(str(watermark_path))
                  .set_duration(final_clip.duration)
                  .resize(height=40)
                  .set_pos(("right","bottom")))
            final_clip = CompositeVideoClip([final_clip, wm])
        except Exception:
            pass

    if out_path is None:
        out_path = TMP / 'final_short.mp4'
    final_clip.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return str(out_path)
