import os
import sys
import traceback
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont  # دي المكتبات اللي كانت ناقصة

# --- 1. دالة المونتاج (المخففة) ---
def create_video(video_paths, audio_path, music_path=None, mode="short", output_path="assets/final_video.mp4"):
    print(f"🎬 STARTING EDIT: Mode={mode} | Clips={len(video_paths)}")
    
    try:
        voice_audio = AudioFileClip(audio_path)
        target_duration = voice_audio.duration + 1.0
        
        clips = []
        current_duration = 0
        
        # إعدادات الجودة (720p للطويل عشان الرامات)
        if mode == "long":
            TARGET_W, TARGET_H = 1280, 720
            print("ℹ️ Config: 720p HD (Optimized for Cloud)")
        else:
            TARGET_W, TARGET_H = 1080, 1920
            print("ℹ️ Config: 1080p Shorts")

        for path in video_paths:
            try:
                clip = VideoFileClip(path)
                
                # Resize Logic
                if mode == "long":
                    # 1. Resize width
                    if clip.w != TARGET_W: 
                        clip = clip.resize(width=TARGET_W)
                    # 2. Crop height
                    if clip.h > TARGET_H:
                        clip = clip.crop(x1=0, y1=clip.h/2 - TARGET_H/2, width=TARGET_W, height=TARGET_H)
                    elif clip.h < TARGET_H:
                        clip = clip.resize(height=TARGET_H)
                        clip = clip.crop(x1=clip.w/2 - TARGET_W/2, y1=0, width=TARGET_W, height=TARGET_H)
                
                else: # Shorts
                    if clip.h != TARGET_H: 
                        clip = clip.resize(height=TARGET_H)
                    if clip.w > TARGET_W:
                        clip = clip.crop(x1=clip.w/2 - TARGET_W/2, y1=0, width=TARGET_W, height=TARGET_H)

                clips.append(clip)
                current_duration += clip.duration
                if current_duration >= target_duration: break
                
            except Exception as e:
                print(f"⚠️ Skipped Bad Clip: {e}")
                continue
        
        if not clips:
            print("❌ ERROR: No valid clips processed!")
            return None

        print(f"🧩 Concatenating {len(clips)} clips...")
        final_clip = concatenate_videoclips(clips, method="compose")
        
        if final_clip.duration > target_duration:
            final_clip = final_clip.subclip(0, target_duration)
        
        # Audio Mix
        final_audio = voice_audio
        if music_path and os.path.exists(music_path):
            print("🎵 Mixing Music...")
            try:
                music = AudioFileClip(music_path)
                if music.duration < target_duration:
                    music = music.loop(duration=target_duration)
                else:
                    music = music.subclip(0, target_duration)
                music = music.volumex(0.15)
                final_audio = CompositeAudioClip([voice_audio, music])
            except Exception as e:
                print(f"⚠️ Music Mix Error: {e}")

        final_clip = final_clip.set_audio(final_audio)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print("💾 Rendering to Disk...")
        final_clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac', 
            threads=1, 
            preset='ultrafast'
        )
        
        return output_path

    except Exception as e:
        print("\n❌ FATAL EDITING CRASH:")
        traceback.print_exc()
        return None

# --- 2. دالة الثامبنيل (اللي كانت ناقصة) ---
def create_thumbnail(image_path, text, output_path="assets/temp/final_thumb.jpg"):
    print("🖼️ Generating Thumbnail...")
    try:
        img = Image.open(image_path)
        img = img.point(lambda p: p * 0.6) # Darken for text
        draw = ImageDraw.Draw(img)
        try:
            # Try to load a bold font available on Linux
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
            
        draw.text((50, 50), text, font=font, fill=(255, 255, 0))
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Thumbnail Saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ Thumbnail Failed: {e}")
        return None
