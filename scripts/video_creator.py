#!/usr/bin/env python3
from pathlib import Path
TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def _import_moviepy():
    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip
        return VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip
    except Exception as e:
        raise ImportError(
            "moviepy import failed. Ensure moviepy and imageio-ffmpeg are installed. "
            "In GH Actions add 'pip install moviepy imageio-ffmpeg' or check logs. Original error: " + str(e)
        )

def assemble_long(clips, voicefile, music=None, title_text=None, outp=None):
    VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip = _import_moviepy()
    clips_objs = []
    for c in clips:
        try:
            v = VideoFileClip(str(c))
            clips_objs.append(v.subclip(0, min(12, v.duration)))
        except Exception:
            continue
    if not clips_objs:
        raise RuntimeError("No valid clips to assemble")
    final = concatenate_videoclips(clips_objs, method='compose')
    # set voice audio
    if voicefile:
        try:
            voice_audio = AudioFileClip(str(voicefile))
            final = final.set_audio(voice_audio)
        except Exception:
            pass
    # optional music mix (simple)
    if music:
        try:
            music_audio = AudioFileClip(str(music)).volumex(0.08)
            final = final.set_audio(voice_audio)
        except Exception:
            pass
    # add CTA text overlay at end
    if title_text:
        try:
            txt = TextClip(title_text, fontsize=36, color='white', bg_color='black', size=final.size)
            txt = txt.set_duration(4).set_pos(('center', 'bottom'))
            final = CompositeVideoClip([final, txt])
        except Exception:
            pass
    outp = outp or TMP / 'final_long.mp4'
    final.write_videofile(str(outp), fps=24, codec='libx264', audio_codec='aac')
    return str(outp)

def assemble_short(clip, music=None, outp=None):
    VideoFileClip, _, AudioFileClip, _, _ = _import_moviepy()
    try:
        v = VideoFileClip(str(clip))
        c = v.subclip(0, min(20, v.duration))
    except Exception as e:
        raise RuntimeError(f"Failed to open short clip {clip}: {e}")
    if music:
        try:
            m = AudioFileClip(str(music)).volumex(0.2)
            c = c.set_audio(m)
        except Exception:
            pass
    outp = outp or TMP / 'final_short.mp4'
    c.write_videofile(str(outp), fps=24, codec='libx264', audio_codec='aac')
    return str(outp)
