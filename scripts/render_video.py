import os
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips

def render_long_video(script_data, audio_paths, media_assets):
    logging.info("Starting Long Video Rendering...")
    clips = []
    
    try:
        for i, asset in enumerate(media_assets):
            video_path = asset['video']
            audio_path = audio_paths[i]
            
            # Verify files exist
            if not os.path.exists(video_path) or not os.path.exists(audio_path):
                logging.warning(f"Missing asset for segment {i}, skipping.")
                continue

            # Load Audio
            audio = AudioFileClip(audio_path)
            
            # Load Video & Resize
            video = VideoFileClip(video_path).resize(height=1080)
            
            # Crop to 16:9 aspect ratio (1920x1080)
            video = video.crop(x1=video.w/2 - 1920/2, y1=0, width=1920, height=1080)

            # Loop video if audio is longer
            if video.duration < audio.duration:
                video = video.loop(duration=audio.duration)
            else:
                video = video.subclip(0, audio.duration)
            
            video = video.set_audio(audio)
            
            # Add Captions (Subtitle)
            # Note: TextClip requires ImageMagick installed in Dockerfile
            txt_clip = TextClip(asset['text'], fontsize=60, color='white', font='DejaVu-Sans-Bold', stroke_color='black', stroke_width=2, method='caption', size=(1600, None))
            txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(video.duration)
            
            final_clip = CompositeVideoClip([video, txt_clip])
            clips.append(final_clip)

        if not clips:
            logging.error("No clips were created! Check media/audio generation.")
            return None

        final_video = concatenate_videoclips(clips, method="compose")
        
        output_path = f"data/output/{script_data['topic'].replace(' ', '_')}_long.mp4"
        final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=4)
        
        logging.info(f"Video Rendered Successfully: {output_path}")
        return output_path

    except Exception as e:
        logging.error(f"Rendering Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def render_shorts(script_data, media_assets):
    # Placeholder for now to focus on Long Video success first
    # If we try to do too much at once, debugging gets hard.
    return [] 