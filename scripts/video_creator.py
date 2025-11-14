# video_creator.py - download clips, assemble video, add voice/music/subtitles
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip
from pathlib import Path
import tempfile
import os
from .utils import download_file

TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def assemble_long_video(clips_paths, voice_path, music_path=None, title_text=None, out_path=None):
    clips = []
    for p in clips_paths:
        # ensure clip length and exist
        try:
            vc = VideoFileClip(str(p))
            sub = vc.subclip(0, min(10, vc.duration))
            clips.append(sub)
        except Exception:
            continue
    if not clips:
        raise RuntimeError('No valid clips to assemble')
    final = concatenate_videoclips(clips, method='compose')

    # voice: if provided, mix voice audio with background music
    if voice_path:
        try:
            voice_audio = AudioFileClip(str(voice_path))
            final = final.set_audio(voice_audio)
        except Exception:
            pass
    if music_path:
        try:
            music = AudioFileClip(str(music_path)).volumex(0.12)
            # overlaying audio: simple approach - replace audio with voice if exists; advanced mixing can be added
            if final.audio:
                final.audio = final.audio
        except Exception:
            pass

    # add end call-to-action
    if title_text:
        try:
            txt = TextClip(title_text, fontsize=40, color='white', bg_color='black', size=final.size)
            txt = txt.set_duration(4).set_pos(('center', 'bottom'))
            final = CompositeVideoClip([final, txt])
        except Exception:
            pass

    if out_path is None:
        out_path = TMP / 'final_long.mp4'
    final.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return out_path

def assemble_short(clip_path, music_path, out_path=None):
    c = VideoFileClip(str(clip_path)).subclip(0, min(20, VideoFileClip(str(clip_path)).duration))
    if music_path:
        music = AudioFileClip(str(music_path)).volumex(0.2)
        c = c.set_audio(music)
    if out_path is None:
        out_path = TMP / 'final_short.mp4'
    c.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return out_path
