# tools/composer.py
from moviepy.editor import *
from pathlib import Path
import random

def compose_long_video(media_folder, audio_path, out_path, facts, cta_text=""):
    # media_folder: folder with images and short clips
    mf = Path(media_folder)
    image_files = sorted(mf.glob(".jpg")) + sorted(mf.glob(".png"))
    video_files = sorted(mf.glob("*.mp4"))
    clip_list = []
    duration_per_fact = None
    # get audio length
    audioclip = AudioFileClip(audio_path)
    total_audio = audioclip.duration
    # choose 11 segments (10 facts + CTA)
    n_segments = max(1, len(facts)+1)
    duration_per_fact = total_audio / n_segments
    # build clips from images and short videos
    i = 0
    for seg in range(n_segments):
        if video_files and random.random() < 0.3:
            vf = video_files[i % len(video_files)]
            clip = VideoFileClip(str(vf)).subclip(0, min(duration_per_fact, VideoFileClip(str(vf)).duration))
        else:
            img = image_files[i % len(image_files)]
            clip = ImageClip(str(img)).set_duration(duration_per_fact)
        clip = clip.fx(vfx.resize, width=1280)
        # add text overlay for the fact if available
        fact_text = facts[seg] if seg < len(facts) else cta_text
        txt = (TextClip(fact_text, fontsize=36, font="DejaVu-Sans", method='caption', size=(1160,80))
               .set_position(("center","bottom")).set_duration(duration_per_fact))
        composed = CompositeVideoClip([clip, txt])
        clip_list.append(composed)
        i+=1
    final = concatenate_videoclips(clip_list, method="compose")
    final = final.set_audio(audioclip)
    final.write_videofile(out_path, codec="libx264", audio_codec="aac", threads=2, fps=24, preset="medium")
    final.close()
    audioclip.close()
    return out_path

def compose_short_video(media_folder, out_path, duration=20):
    mf = Path(media_folder)
    image_files = sorted(mf.glob(".jpg")) + sorted(mf.glob(".png"))
    video_files = sorted(mf.glob("*.mp4"))
    clips = []
    total = duration
    part = max(1, total // max(1, (len(image_files)+len(video_files))))
    # use videos if available else images
    for idx in range(int(total/part)+1):
        if video_files and idx < len(video_files):
            c = VideoFileClip(str(video_files[idx])).subclip(0, min(part, VideoFileClip(str(video_files[idx])).duration))
        else:
            img = image_files[idx % len(image_files)]
            c = ImageClip(str(img)).set_duration(part)
        c = c.fx(vfx.resize, width=1080)
        clips.append(c)
    final = concatenate_videoclips(clips, method="compose").set_fps(30)
    # add background music: not specified here; later can add music track if desired
    final.write_videofile(out_path, codec="libx264", audio_codec="aac", threads=2, fps=30, preset="medium")
    final.close()
    return out_path
