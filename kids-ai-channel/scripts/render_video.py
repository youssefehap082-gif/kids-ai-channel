from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import os

def render_long_video(script_data, audio_paths, media_assets):
    clips = []
    
    for i, asset in enumerate(media_assets):
        video_path = asset['video']
        audio_path = audio_paths[i]
        
        try:
            audio = AudioFileClip(audio_path)
            video = VideoFileClip(video_path).resize(height=1080)
            
            # Loop video if audio is longer
            if video.duration < audio.duration:
                video = video.loop(duration=audio.duration)
            else:
                video = video.subclip(0, audio.duration)
            
            video = video.set_audio(audio)
            
            # Add simple subtitle
            txt_clip = TextClip(asset['text'], fontsize=50, color='white', font='Arial-Bold', stroke_color='black', stroke_width=2)
            txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(video.duration)
            
            final_clip = CompositeVideoClip([video, txt_clip])
            clips.append(final_clip)
        except Exception as e:
            print(f"Skipping clip {i} due to error: {e}")
            continue

    if not clips:
        return None

    final_video = concatenate_videoclips(clips, method="compose")
    output_path = f"data/output/{script_data['topic']}_long.mp4"
    os.makedirs("data/output", exist_ok=True)
    final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    return output_path

def render_shorts(script_data, media_assets):
    # Simplified Shorts Logic (Center Crop + Fast Pacing)
    return [] # Returning empty for safety in this generator
