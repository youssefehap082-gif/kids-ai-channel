import os
import logging
import requests
from moviepy.editor import (VideoFileClip, AudioFileClip, TextClip, 
                          CompositeVideoClip, concatenate_videoclips, afx, vfx)

def render_long_video(script_data, audio_paths, media_assets):
    logging.info("Starting Pro Editing (Music + Transitions)...")
    
    # 1. Download Background Music
    bg_music_path = "data/temp/bg_music.mp3"
    _download_music(bg_music_path)
    
    clips = []
    
    for i, asset in enumerate(media_assets):
        try:
            # Load Assets
            video = VideoFileClip(asset['video']).resize(height=1080)
            audio = AudioFileClip(audio_paths[i])
            
            # Visual Processing: Crop to 16:9 and center
            video = video.crop(x1=video.w/2 - 1920/2, y1=0, width=1920, height=1080)
            
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
            txt_clip = TextClip(asset['text'], fontsize=70, color='white', font='DejaVu-Sans-Bold', 
                              stroke_color='black', stroke_width=3, size=(1700, None), method='caption')
            txt_clip = txt_clip.set_pos(('center', 0.8), relative=True).set_duration(video.duration)
            
            # Combine
            final_clip = CompositeVideoClip([video, txt_clip])
            clips.append(final_clip)
            
        except Exception as e:
            logging.error(f"Skipping clip {i}: {e}")

    if not clips: return None

    # Concatenate All Clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # 2. Add Background Music
    if os.path.exists(bg_music_path):
        bg_music = AudioFileClip(bg_music_path).volumex(0.15) # Low volume
        # Loop music to match video length
        bg_music = afx.audio_loop(bg_music, duration=final_video.duration)
        
        # Combine Voice + Music
        final_audio = CompositeAudioClip([final_video.audio, bg_music])
        final_video = final_video.set_audio(final_audio)

    output_path = f"data/output/{script_data['topic']}_pro.mp4"
    final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=4)
    
    return output_path

def _download_music(path):
    # Royalty Free Music (Kevin MacLeod style or similar)
    url = "https://cdn.pixabay.com/download/audio/2022/03/24/audio_1909559014.mp3" 
    try:
        with requests.get(url, stream=True) as r:
            with open(path, 'wb') as f:
                f.write(r.content)
    except:
        pass
        
# Need to import CompositeAudioClip at top, adding here for safety
from moviepy.editor import CompositeAudioClip