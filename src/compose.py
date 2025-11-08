import os, tempfile, random, glob
from pathlib import Path
from typing import List
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from pydub import AudioSegment

def download_files(urls: List[str], workdir: Path) -> List[Path]:
    import requests
    paths = []
    for i, u in enumerate(urls):
        r = requests.get(u, timeout=300)
        r.raise_for_status()
        p = workdir / f"clip_{i}.mp4"
        p.write_bytes(r.content)
        paths.append(p)
    return paths

def pick_bg_music(music_dir: Path) -> Path | None:
    tracks = list(music_dir.glob("*.mp3"))
    return random.choice(tracks) if tracks else None

def make_voicebed(voice_paths: List[Path], bg_music: Path | None = None, music_gain_db=-18) -> Path:
    narration = AudioSegment.silent(duration=0)
    for p in voice_paths:
        narration += AudioSegment.from_file(p)
    if bg_music:
        music = AudioSegment.from_file(bg_music) - abs(music_gain_db)
        # loop music to narration length
        looped = (music * (int(len(narration) / len(music)) + 2))[:len(narration)]
        mix = looped.overlay(narration)
        out = mix
    else:
        out = narration
    out_path = Path(tempfile.mkdtemp()) / "voicebed.mp3"
    out.export(out_path, format="mp3")
    return out_path

def compose_video(video_paths: List[Path], audio_path: Path, min_duration=185) -> Path:
    clips = []
    for p in video_paths:
        c = VideoFileClip(str(p)).fx(vfx.resize, height=1080)
        clips.append(c)
    seq, cur, i = [], 0, 0
    while cur < min_duration and clips:
        c = clips[i % len(clips)]
        take = min(c.duration, max(5, min_duration - cur))
        seq.append(c.subclip(0, take))
        cur += take
        i += 1
    final = concatenate_videoclips(seq, method="compose").set_audio(AudioFileClip(str(audio_path)))
    out_path = Path(tempfile.mkdtemp()) / "final_video.mp4"
    final.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="6000k")
    for c in clips: c.close()
    return out_path

def compose_short(video_paths: List[Path], audio_path: Path, target_duration=58) -> Path:
    clips = []
    for p in video_paths:
        c = VideoFileClip(str(p)).resize(height=1920)
        if c.w > 1080:
            x = int((c.w - 1080) / 2)
            c = c.crop(x1=x, y1=0, x2=x+1080, y2=1920)
        clips.append(c)
    seq, cur = [], 0
    for c in clips:
        take = min(c.duration, max(2, target_duration - cur))
        seq.append(c.subclip(0, take))
        cur += take
        if cur >= target_duration: break
    final = concatenate_videoclips(seq, method="compose").set_audio(AudioFileClip(str(audio_path)))
    out_path = Path(tempfile.mkdtemp()) / "short.mp4"
    final.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="4000k")
    for c in clips: c.close()
    return out_path
