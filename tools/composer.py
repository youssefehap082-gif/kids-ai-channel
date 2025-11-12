# tools/composer.py
from moviepy.editor import *
from pathlib import Path
import random
import os

def compose_long_video(media_folder, audio_path, out_path, facts, background_music=None, cta_text="Don't forget to subscribe and hit the bell for more!"):
    mf = Path(media_folder)
    image_files = sorted(mf.glob(".jpg")) + sorted(mf.glob(".png"))
    video_files = sorted(mf.glob("*.mp4"))
    clips = []
    # load audio
    audioclip = AudioFileClip(audio_path) if Path(audio_path).exists() else None
    total_audio = audioclip.duration if audioclip else max(30, len(facts)*5)
    n_segments = max(1, len(facts) + 1)
    seg_dur = total_audio / n_segments

    i = 0
    for idx in range(n_segments):
        if video_files and random.random() < 0.35:
            vf = video_files[i % len(video_files)]
            try:
                vclip = VideoFileClip(str(vf)).subclip(0, min(seg_dur, VideoFileClip(str(vf)).duration))
            except:
                vclip = ImageClip(str(image_files[i % len(image_files)])).set_duration(seg_dur)
        else:
            img = image_files[i % len(image_files)] if image_files else None
            if img:
                vclip = ImageClip(str(img)).set_duration(seg_dur)
            else:
                # blank clip fallback
                vclip = ColorClip(size=(1280,720), color=(0,0,0)).set_duration(seg_dur)
        vclip = vclip.resize(width=1280)
        # overlay text
        fact_text = facts[idx] if idx < len(facts) else cta_text
        txt = (TextClip(fact_text, fontsize=36, font="DejaVu-Sans", method='caption', size=(1160,120))
               .set_position(("center","bottom")).set_duration(seg_dur))
        composed = CompositeVideoClip([vclip, txt])
        clips.append(composed)
        i += 1

    final = concatenate_videoclips(clips, method="compose")
    if audioclip:
        final = final.set_audio(audioclip)
    # add background music if provided (mixed)
    if background_music and Path(background_music).exists():
        try:
            music = AudioFileClip(background_music).volumex(0.15)
            if final.audio:
                new_audio = CompositeAudioClip([final.audio, music.set_duration(final.duration)])
            else:
                new_audio = music.set_duration(final.duration)
            final = final.set_audio(new_audio)
        except Exception:
            pass

    final.write_videofile(out_path, codec="libx264", audio_codec="aac", threads=2, fps=24, preset="medium")
    final.close()
    if audioclip:
        audioclip.close()
    return out_path

def compose_short_video(media_folder, out_path, duration=20):
    mf = Path(media_folder)
    image_files = sorted(mf.glob(".jpg")) + sorted(mf.glob(".png"))
    video_files = sorted(mf.glob("*.mp4"))
    clips = []
    remaining = duration
    idx = 0
    while remaining > 0:
        part = min(5, remaining)
        if video_files and idx < len(video_files):
            try:
                c = VideoFileClip(str(video_files[idx])).subclip(0, min(part, VideoFileClip(str(video_files[idx])).duration))
            except:
                if image_files:
                    c = ImageClip(str(image_files[idx % len(image_files)])).set_duration(part)
                else:
                    c = ColorClip(size=(1080,1920), color=(0,0,0)).set_duration(part)
        else:
            if image_files:
                c = ImageClip(str(image_files[idx % len(image_files)])).set_duration(part)
            else:
                c = ColorClip(size=(1080,1920), color=(0,0,0)).set_duration(part)
        c = c.resize(width=1080)
        clips.append(c)
        remaining -= part
        idx += 1
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(out_path, codec="libx264", audio_codec="aac", threads=2, fps=30, preset="medium")
    final.close()
    return out_path
