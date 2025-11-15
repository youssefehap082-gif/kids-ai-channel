from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip, ImageClip
from pathlib import Path
import tempfile, os

TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def assemble_long_video(clips_paths, voice_path=None, music_path=None, title_text=None, watermark_path=None, out_path=None, target_duration=180):
    clips = []
    total = 0.0
    for p in clips_paths:
        try:
            v = VideoFileClip(str(p))
            length = min(v.duration, 15)
            clips.append(v.subclip(0, length))
            total += length
            if total >= target_duration:
                break
        except Exception:
            continue
    if not clips:
        raise RuntimeError('No valid clips to assemble')
    final = concatenate_videoclips(clips, method='compose')
    if voice_path and Path(voice_path).exists():
        voice_audio = AudioFileClip(str(voice_path))
        final = final.set_audio(voice_audio.set_duration(final.duration))
    if music_path and Path(music_path).exists():
        try:
            music = AudioFileClip(str(music_path)).volumex(0.10)
            if not voice_path:
                final = final.set_audio(music.set_duration(final.duration))
        except Exception:
            pass
    if title_text:
        txt = TextClip(title_text, fontsize=48, color='white', bg_color='black', size=final.size)
        txt = txt.set_duration(4).set_pos(('center','bottom'))
        final = CompositeVideoClip([final, txt])
    if watermark_path and Path(watermark_path).exists():
        try:
            wm = (ImageClip(str(watermark_path))
                  .set_duration(final.duration)
                  .resize(height=60)
                  .margin(right=8, bottom=8, opacity=0)
                  .set_pos(("right", "bottom")))
            final = CompositeVideoClip([final, wm])
        except Exception:
            pass
    if out_path is None:
        out_path = TMP / 'final_long.mp4'
    final.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return str(out_path)

def assemble_short(clips_paths, voice_path=None, music_path=None, watermark_path=None, out_path=None, max_duration=60):
    clips = []
    total = 0.0
    for p in clips_paths:
        try:
            v = VideoFileClip(str(p))
            cut = v.subclip(0, min(5, v.duration))
            clips.append(cut)
            total += cut.duration
            if total >= max_duration:
                break
        except Exception:
            continue
    if not clips:
        raise RuntimeError('No valid clips for short video.')
    base = concatenate_videoclips(clips, method='compose').subclip(0, min(max_duration, sum(c.duration for c in clips)))
    if voice_path and Path(voice_path).exists():
        try:
            voice_audio = AudioFileClip(str(voice_path))
            if base.duration >= voice_audio.duration:
                base = base.subclip(0, voice_audio.duration)
            else:
                loops = int(voice_audio.duration // base.duration) + 1
                base = concatenate_videoclips([base] * loops).subclip(0, voice_audio.duration)
            base = base.set_audio(voice_audio.set_duration(base.duration))
        except Exception:
            pass
    elif music_path and Path(music_path).exists():
        try:
            music = AudioFileClip(str(music_path)).volumex(0.15)
            base = base.set_audio(music.set_duration(base.duration))
        except Exception:
            pass
    if watermark_path and Path(watermark_path).exists():
        try:
            wm = (ImageClip(str(watermark_path))
                  .set_duration(base.duration)
                  .resize(height=40)
                  .set_pos(("right","bottom")))
            base = CompositeVideoClip([base, wm])
        except Exception:
            pass
    if out_path is None:
        out_path = TMP / 'final_short.mp4'
    base.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return str(out_path)
