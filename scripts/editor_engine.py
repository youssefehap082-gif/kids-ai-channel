import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

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
                try:
                    # Load clip
                    clip = VideoFileClip(path)
                    
                    # Resize logic: 
                    # 1. Resize height to 1920 (HD Vertical)
                    if clip.h != 1920:
                        clip = clip.resize(height=1920)
                    
                    # 2. Crop the center to get width 1080
                    if clip.w > 1080:
                        x_center = clip.w / 2
                        clip = clip.crop(x1=x_center - 540, y1=0, width=1080, height=1920)
                    elif clip.w < 1080:
                        # If too thin, resize width (less common but safe)
                        clip = clip.resize(width=1080)
                        clip = clip.crop(x1=0, y1=0, width=1080, height=1920)
                    
                    clips.append(clip)
                    current_duration += clip.duration
                    if current_duration >= target_duration:
                        break
                except Exception as e:
                    print(f"⚠️ Skipping bad clip {path}: {e}")
                    continue
        
        if not clips:
            print("❌ No valid clips found for editing.")
            return None

        # Concatenate using the CORRECT function name (lowercase)
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Trim to audio length
        final_clip = final_clip.subclip(0, target_duration)
        
        # Add Audio
        final_clip = final_clip.set_audio(audio)
        
        # Export
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Lower threads to prevent memory crash on free GitHub runners
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=1, preset='ultrafast')
        print(f"✅ Video Rendered: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Editing Error: {e}")
        return None
