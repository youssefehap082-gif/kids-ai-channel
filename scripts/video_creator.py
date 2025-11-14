from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip
from pathlib import Path
TMP = Path(__file__).resolve().parent / 'tmp_video'
TMP.mkdir(parents=True, exist_ok=True)
def assemble_long_video(clips, voice_path=None, music_path=None, title_text=None, out=None):
    vids = []
    for p in clips:
        try:
            v = VideoFileClip(str(p))
            vids.append(v.subclip(0, min(10, v.duration)))
        except Exception:
            continue
    if not vids: raise RuntimeError('No clips')
    final = concatenate_videoclips(vids, method='compose')
    if voice_path:
        final = final.set_audio(AudioFileClip(str(voice_path)))
    if title_text:
        txt = TextClip(title_text, fontsize=40, color='white', bg_color='black', size=final.size).set_duration(4).set_pos(('center','bottom'))
        final = CompositeVideoClip([final, txt])
    if out is None: out = TMP / 'long.mp4'
    final.write_videofile(str(out), fps=24, codec='libx264', audio_codec='aac')
    return out
def assemble_short(clip, music=None, out=None):
    v = VideoFileClip(str(clip))
    c = v.subclip(0, min(20, v.duration))
    if music:
        c = c.set_audio(AudioFileClip(str(music)))
    if out is None: out = TMP / 'short.mp4'
    c.write_videofile(str(out), fps=24, codec='libx264', audio_codec='aac')
    return out
