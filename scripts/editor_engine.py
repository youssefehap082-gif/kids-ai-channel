import os
import traceback # عشان نعرف الغلطة فين بالظبط
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip

def create_video(video_paths, audio_path, music_path=None, mode="short", output_path="assets/final_video.mp4"):
    print(f"🎬 Editing Video (Mode: {mode}) - High Quality...")
    
    try:
        voice_audio = AudioFileClip(audio_path)
        target_duration = voice_audio.duration + 1.0
        
        clips = []
        current_duration = 0
        
        # Loop through videos
        for path in video_paths:
            try:
                clip = VideoFileClip(path)
                
                if mode == "short":
                     # Portrait 9:16 (1080x1920)
                     if clip.h != 1920: clip = clip.resize(height=1920)
                     if clip.w > 1080:
                        clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
                else:
                     # Landscape 16:9 (1920x1080) - FULL HD
                     # 1. Resize width to 1920
                     if clip.w != 1920: clip = clip.resize(width=1920)
                     
                     # 2. Crop height to 1080 (centered)
                     if clip.h > 1080:
                        clip = clip.crop(x1=0, y1=clip.h/2 - 540, width=1920, height=1080)
                     elif clip.h < 1080:
                        # If too short, resize height then crop width
                        clip = clip.resize(height=1080)
                        clip = clip.crop(x1=clip.w/2 - 960, y1=0, width=1920, height=1080)

                clips.append(clip)
                current_duration += clip.duration
                if current_duration >= target_duration: break
            except Exception as e:
                print(f"⚠️ Warning: Problem with clip {path}: {e}")
                continue
        
        if not clips: 
            print("❌ No valid clips to process.")
            return None

        print("🧩 Concatenating clips...")
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Trim
        if final_clip.duration > target_duration:
            final_clip = final_clip.subclip(0, target_duration)
        
        # Audio Mix
        final_audio = voice_audio
        if music_path and os.path.exists(music_path):
            print("🎵 Mixing Audio...")
            try:
                music = AudioFileClip(music_path)
                if music.duration < target_duration:
                    music = music.loop(duration=target_duration)
                else:
                    music = music.subclip(0, target_duration)
                
                music = music.volumex(0.15) # 15% volume
                final_audio = CompositeAudioClip([voice_audio, music])
            except Exception as e:
                print(f"⚠️ Audio Mix Warning: {e}")

        final_clip = final_clip.set_audio(final_audio)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print("💾 Rendering Final Video (This may take time)...")
        # High Quality Render
        final_clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac', 
            threads=2, 
            preset='ultrafast' # بنستخدم ultrafast عشان ننجز، بس الجودة هتفضل 1080
        )
        
        return output_path
        
    except Exception as e:
        print("\n❌ FATAL EDITING ERROR:")
        print("-" * 30)
        traceback.print_exc() # ده السطر اللي هيفضح السبب
        print("-" * 30)
        return None
