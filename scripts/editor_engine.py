import os
# استيراد المكتبات اللازمة للصوت
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip

def create_video(video_paths, audio_path, music_path=None, output_path="assets/final_video.mp4"):
    print("🎬 Editing Video (With Music)...")
    
    try:
        # 1. تجهيز صوت المذيع
        voice_audio = AudioFileClip(audio_path)
        target_duration = voice_audio.duration + 1 # بنزود ثانية عشان الهدوء
        
        # 2. تجهيز الفيديوهات
        clips = []
        current_duration = 0
        
        while current_duration < target_duration:
            for path in video_paths:
                try:
                    clip = VideoFileClip(path)
                    # Resize to Shorts (1080x1920)
                    if clip.h != 1920: clip = clip.resize(height=1920)
                    if clip.w > 1080:
                        x_center = clip.w / 2
                        clip = clip.crop(x1=x_center - 540, y1=0, width=1080, height=1920)
                    
                    clips.append(clip)
                    current_duration += clip.duration
                    if current_duration >= target_duration: break
                except: continue
        
        if not clips: return None

        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.subclip(0, target_duration)
        
        # 3. دمج الصوت (المذيع + الموسيقى)
        final_audio = voice_audio
        
        if music_path and os.path.exists(music_path):
            try:
                music = AudioFileClip(music_path)
                # تكرار الموسيقى لو الفيديو طويل
                if music.duration < target_duration:
                    music = music.loop(duration=target_duration)
                else:
                    music = music.subclip(0, target_duration)
                
                # توطية صوت الموسيقى لـ 10% عشان المذيع يبان
                music = music.volumex(0.1)
                
                # دمج الاثنين
                final_audio = CompositeAudioClip([voice_audio, music])
                print("✅ Background Music Added & Mixed.")
            except Exception as e:
                print(f"⚠️ Music mix failed, using voice only: {e}")

        # تركيب الصوت النهائي على الفيديو
        final_clip = final_clip.set_audio(final_audio)
        
        # Export
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=1, preset='ultrafast')
        
        return output_path
        
    except Exception as e:
        print(f"❌ Editing Error: {e}")
        return None
