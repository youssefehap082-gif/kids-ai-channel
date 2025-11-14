import os
from scripts.moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    AudioFileClip,
    CompositeVideoClip,
    TextClip
)
from scripts.utils import download_videos, merge_audio, save_temp
from pathlib import Path

TEMP = Path("temp")
TEMP.mkdir(exist_ok=True)

def assemble_long_video(clips, audio_path, captions):
    video_clips = [VideoFileClip(clip).resize((1280, 720)) for clip in clips]

    final_video = concatenate_videoclips(video_clips, method="compose")
    audio = AudioFileClip(audio_path)

    final_video = final_video.set_audio(audio)

    # Add captions
    caption_clips = []
    y = 600

    for line in captions:
        txt = TextClip(
            txt=line,
            fontsize=48,
            color="white",
            stroke_color="black",
            stroke_width=1,
            method="label"
        ).set_duration(final_video.duration).set_position(("center", y))
        caption_clips.append(txt)
        y += 60

    output = CompositeVideoClip([final_video] + caption_clips)

    out_path = save_temp("long_final.mp4")
    output.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac")

    return out_path


def assemble_short(clips, music_path):
    video_clips = [VideoFileClip(clip).resize((1080, 1920)) for clip in clips]

    final_video = concatenate_videoclips(video_clips, method="compose")

    music = AudioFileClip(music_path).volumex(0.8)
    final_video = final_video.set_audio(music)

    out_path = save_temp("short_final.mp4")
    final_video.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac")

    return out_path
