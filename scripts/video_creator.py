from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, ImageClip
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile, os

TMP = Path(__file__).resolve().parent / 'tmp'
TMP.mkdir(exist_ok=True)

def make_title_image(text, width, height=120, fontsize=48, font_path=None):
    # create transparent image with centered text
    img = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path or 'DejaVuSans-Bold.ttf', fontsize)
    except Exception:
        font = ImageFont.load_default()
    w, h = draw.textsize(text, font=font)
    draw.rectangle([(0,0),(width,height)], fill=(0,0,0,180))
    draw.text(((width-w)/2,(height-h)/2), text, font=font, fill=(255,255,255,255))
    out = TMP / f"title_{abs(hash(text))%100000}.png"
    img.save(out)
    return str(out)

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
    # set audio: voice (preferred) then music as background if needed
    if voice_path and Path(voice_path).exists():
        voice_audio = AudioFileClip(str(voice_path))
        final = final.set_audio(voice_audio.set_duration(final.duration))
    else:
        if music_path and Path(music_path).exists():
            music = AudioFileClip(str(music_path)).volumex(0.10)
            final = final.set_audio(music.set_duration(final.duration))
    # Title overlay for first 4 seconds
    if title_text:
        title_img = make_title_image(title_text, final.size[0], height=120, fontsize=48)
        title_clip = ImageClip(title_img).set_duration(4).set_pos(('center','top'))
        final = CompositeVideoClip([final, title_clip])
    # watermark at right-bottom with 30% opacity
    if watermark_path and Path(watermark_path).exists():
        try:
            wm = (ImageClip(str(watermark_path))
                  .set_duration(final.duration)
                  .resize(height=60)
                  .set_opacity(0.3)
                  .set_pos(('right','bottom')))
            final = CompositeVideoClip([final, wm])
        except Exception:
            pass
    if out_path is None:
        out_path = TMP / 'final_long.mp4'
    final.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return str(out_path)

def assemble_short(clips_paths, voice_path=None, music_path=None, watermark_path=None, out_path=None, voice_duration=15, max_duration=60):
    # Build base video by concatenating short slices until at least max_duration or clips exhausted.
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
    base = concatenate_videoclips(clips, method='compose')
    # prepare voice: trim or pad to voice_duration
    if voice_path and Path(voice_path).exists():
        try:
            voice_audio = AudioFileClip(str(voice_path))
            # take first voice_duration seconds of voice_audio
            voice_segment = voice_audio.subclip(0, min(voice_duration, voice_audio.duration))
            # set base to have at least voice_duration length
            if base.duration < voice_segment.duration:
                loops = int(voice_segment.duration // base.duration) + 1
                base = concatenate_videoclips([base] * loops).subclip(0, voice_segment.duration)
            base = base.set_audio(voice_segment.set_duration(base.duration))
            # after voice finishes, append music if space remains
            if max_duration > base.duration and music_path and Path(music_path).exists():
                music = AudioFileClip(str(music_path)).subclip(0, max_duration - base.duration).volumex(0.15)
                # create silent video segment to hold music if needed
                base = base.set_audio(voice_segment)  # voice during initial part
                # mix music for remaining duration by concatenating a silent clip visual with music audio
                # simplest approach: extend base audio by concatenating music to existing audio track when uploading
        except Exception:
            pass
    else:
        # no voice: fill with music up to max_duration
        if music_path and Path(music_path).exists():
            music = AudioFileClip(str(music_path)).subclip(0, min(max_duration, base.duration)).volumex(0.15)
            base = base.set_audio(music.set_duration(base.duration))
    # watermark
    if watermark_path and Path(watermark_path).exists():
        try:
            wm = (ImageClip(str(watermark_path))
                  .set_duration(base.duration)
                  .resize(height=40)
                  .set_opacity(0.3)
                  .set_pos(('right','bottom')))
            base = CompositeVideoClip([base, wm])
        except Exception:
            pass
    if out_path is None:
        out_path = TMP / 'final_short.mp4'
    # ensure duration not exceeding max_duration
    base = base.subclip(0, min(max_duration, base.duration))
    base.write_videofile(str(out_path), fps=24, codec='libx264', audio_codec='aac')
    return str(out_path)
