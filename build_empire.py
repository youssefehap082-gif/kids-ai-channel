import os
import json

# ==========================================
# PHASE 3.1: FIXING THE EDITOR BUG
# ==========================================

PROJECT_NAME = "." 

def create_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Fixed: {path}")

def main():
    print("🚀 APPLYING EDITOR PATCH...")

    # 1. EDITOR ENGINE (FIXED IMPORT NAME)
    editor_engine = """
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
                    clip = VideoFileClip(path)
                    # Resize to vertical 9:16 (1080x1920)
                    # Resize height first
                    clip = clip.resize(height=1920)
                    # Crop center
                    x_center = clip.w / 2
                    clip = clip.crop(x1=x_center - 540, y1=0, width=1080, height=1920)
                    
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

        # Concatenate (Fixed Function Name)
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Trim to audio length
        final_clip = final_clip.subclip(0, target_duration)
        
        # Add Audio
        final_clip = final_clip.set_audio(audio)
        
        # Export
        # Ensure output dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=4)
        print(f"✅ Video Rendered: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Editing Error: {e}")
        import traceback
        traceback.print_exc()
        return None
"""
    create_file("scripts/editor_engine.py", editor_engine)

    print("\n✅ EDITOR PATCH APPLIED. READY TO RETRY.")

if __name__ == "__main__":
    main()
