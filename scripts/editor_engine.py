
import os
from moviepy.editor import VideoFileClip, AudioFileClip, ConcatenateVideoClip, vfx

def create_video(video_paths, audio_path, output_path="assets/final_video.mp4"):
    print("🎬 Editing Video...")
    
    try:
        # Load Audio to get duration
        audio = AudioFileClip(audio_path)
        target_duration = audio.duration
        
        clips = []
        current_duration = 0
        
        # Load and loop videos to match audio
        while current_duration < target_duration:
            for path in video_paths:
                clip = VideoFileClip(path)
                # Resize to vertical 9:16 if needed (basic crop)
                clip = clip.resize(height=1920)
                clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
                
                clips.append(clip)
                current_duration += clip.duration
                if current_duration >= target_duration:
                    break
        
        # Concatenate
        final_clip = ConcatenateVideoClip(clips)
        # Trim to audio length
        final_clip = final_clip.subclip(0, target_duration)
        # Add Audio
        final_clip = final_clip.set_audio(audio)
        
        # Export
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        print(f"✅ Video Rendered: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Editing Error: {e}")
        return None
