import os
import logging
import requests
from moviepy.editor import (VideoFileClip, AudioFileClip, TextClip, 
                          CompositeVideoClip, concatenate_videoclips, afx, vfx, CompositeAudioClip)

def render_long_video(script_data, audio_paths, media_assets):
    logging.info("Starting Pro Editing (Music + Transitions)...")
    
    # 1. Download Background Music
    bg_music_path = "data/temp/bg_music.mp3"
    _download_music(bg_music_path)
    
    clips = []
    
    for i, asset in enumerate(media_assets):
        try:
            # Verify files exist
            if not os.path.exists(asset['video']) or not os.path.exists(audio_paths[i]):
                logging.warning(f"Missing files for segment {i}, skipping.")
                continue

            # Load Assets
            video = VideoFileClip(asset['video']).resize(height=1080)
            audio = AudioFileClip(audio_paths[i])
            
            # Visual Processing: Crop to 16:9 (1920x1080)
            # Try-catch for crop in case video is small
            try:
                if video.w > 1920:
                    video = video.crop(x1=video.w/2 - 1920/2, y1=0, width=1920, height=1080)
                else:
                    video = video.resize(width=1920)
                    video = video.crop(y1=video.h/2 - 1080/2, height=1080)
            except:
                video = video.resize(newsize=(1920, 1080))

            # Duration Sync
            if video.duration < audio.duration:
                video = video.loop(duration=audio.duration)
            else:
                video = video.subclip(0, audio.duration)
            
            # Set Audio (Voice)
            video = video.set_audio(audio)
            
            # Add Fade Transition
            video = video.fx(vfx.fadein, 0.5).fx(vfx.fadeout, 0.5)

            # Add Text (Subtitle) with Shadow
            try:
                txt_clip = TextClip(asset['text'], fontsize=70, color='white', font='DejaVu-Sans-Bold', 
                                  stroke_color='black', stroke_width=3, size=(1700, None), method='caption')
                txt_clip = txt_clip.set_pos(('center', 0.8), relative=True).set_duration(video.duration)
                final_clip = CompositeVideoClip([video, txt_clip])
            except Exception as e:
                logging.error(f"TextClip error: {e}. Using video without text.")
                final_clip = video
            
            clips.append(final_clip)
            
        except Exception as e:
            logging.error(f"Skipping clip {i}: {e}")

    if not clips:
        logging.error("No clips created.")
        return None

    # Concatenate All Clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # 2. Add Background Music
    if os.path.exists(bg_music_path) and os.path.getsize(bg_music_path) > 1000:
        try:
            bg_music = AudioFileClip(bg_music_path).volumex(0.10) # Very Low volume
            # Loop music to match video length
            bg_music = afx.audio_loop(bg_music, duration=final_video.duration)
            
            # Combine Voice + Music
            final_audio = CompositeAudioClip([final_video.audio, bg_music])
            final_video = final_video.set_audio(final_audio)
        except Exception as e:
            logging.error(f"Music mix failed: {e}. Proceeding without music.")

    output_path = f"data/output/{script_data['topic'].replace(' ', '_')}_pro.mp4"
    final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=4)
    
    return output_path

def _download_music(path):
    # Direct reliable link (Royalty Free)
    url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" 
    try:
        logging.info("Downloading Background Music...")
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info("Music Downloaded Successfully.")
    except Exception as e:
        logging.error(f"Music download failed: {e}")
        # Remove bad file if exists
        if os.path.exists(path): os.remove(path)

def render_shorts(script_data, media_assets):
    return [] 