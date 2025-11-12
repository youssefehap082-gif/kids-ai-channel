# المسار: src/main.py

import os
import shutil
from datetime import datetime, timedelta
from moviepy.editor import concatenate_audioclips, AudioFileClip

from src import ai_content, audio_generation, video_assembly, youtube_uploader, state_manager
from src.config import ASSETS_DIR

# --- إعدادات الجدولة (للتشغيل الفعلي) ---
# التوقيتات دي بتستهدف (بتوقيت UTC):
# 1 PM UTC = 9 AM (New York) - 6 AM (Los Angeles)
# 7 PM UTC = 3 PM (New York) - 12 PM (Los Angeles)
# الشورتات بتبقى بين الفيديوهات الطويلة
SCHEDULE_TIMES_UTC = [
    13, # 1 PM UTC - Short 1
    14, # 2 PM UTC - Long Video 1
    15, # 3 PM UTC - Short 2
    17, # 5 PM UTC - Short 3
    19, # 7 PM UTC - Long Video 2
    20, # 8 PM UTC - Short 4
    21  # 9 PM UTC - Short 5
]

def get_schedule_time(index: int) -> datetime:
    """
    يحسب ميعاد النشر بتوقيت UTC
    """
    now = datetime.utcnow()
    # لو الساعة عدت آخر ميعاد، انشر لبكرة
    if now.hour >= SCHEDULE_TIMES_UTC[-1]:
        day = now.date() + timedelta(days=1)
    else:
        day = now.date()
    
    hour = SCHEDULE_TIMES_UTC[index]
    return datetime(day.year, day.month, day.day, hour, 0, 0)

def cleanup():
    """ينضف فولدر الـ assets بعد كل فيديو"""
    print("Cleaning up assets directory...")
    if os.path.exists(ASSETS_DIR):
        shutil.rmtree(ASSETS_DIR)
    os.makedirs(ASSETS_DIR, exist_ok=True)

def run_long_video_workflow(animal: str, gender: str, schedule_time: datetime):
    """
    الخطوات الكاملة لإنشاء ورفع فيديو طويل
    """
    print(f"\n--- 🎬 STARTING LONG VIDEO WORKFLOW: {animal} ({gender}) ---")
    try:
        # 1. إنشاء السكريبت و الـ SEO
        metadata = ai_content.generate_long_video_script(animal)
        facts = metadata['facts']
        
        # 2. إنشاء التعليق الصوتي
        vo_files, vo_durations = audio_generation.generate_all_vo_files(facts, gender)
        
        # 3. جلب الموسيقى
        music_file = audio_generation.get_copyright_free_music()
        
        # 4. تجميع الفيديو
        video_path = video_assembly.assemble_long_video(
            animal, facts, vo_files, vo_durations, music_file
        )
        
        # 5. رفع الفيديو
        video_id = youtube_uploader.schedule_video_upload(
            video_path, metadata, schedule_time, is_short=False
        )
        
        if not video_id:
            raise Exception("Video upload failed, skipping subtitles.")
            
        # 6. تجهيز ملفات الترجمة (ده من متطلباتك الأساسية)
        
        # 6a. دمج كل الصوتيات في ملف واحد لـ Whisper
        combined_vo_path = os.path.join(ASSETS_DIR, "combined_vo.mp3")
        audio_clips = [AudioFileClip(f) for f in vo_files]
        combined_audio = concatenate_audioclips(audio_clips)
        combined_audio.write_audiofile(combined_vo_path)

        # 6b. إنشاء الـ SRT بالإنجليزي
        srt_en = youtube_uploader.generate_srt_from_audio(combined_vo_path)
        if not srt_en:
            raise Exception("SRT generation failed.")
            
        # 6c. رفع الـ SRT بالإنجليزي
        youtube_uploader.upload_subtitle(video_id, srt_en, "en")
        
        # 6d. الترجمة والرفع للغات التانية (لزيادة الربح)
        languages_to_translate = {
            "es": "Spanish",
            "de": "German",
            "fr": "French",
            "hi": "Hindi" # لغة مهمة لزيادة المشاهدات
        }
        
        for lang_code, lang_name in languages_to_translate.items():
            translated_srt = ai_content.translate_srt(srt_en, lang_code, lang_name)
            youtube_uploader.upload_subtitle(video_id, translated_srt, lang_code)
            
        print(f"--- ✅ LONG VIDEO WORKFLOW SUCCESS: {animal} ---")
        return True

    except Exception as e:
        print(f"--- ❌ LONG VIDEO WORKFLOW FAILED: {animal} ---")
        print(f"Error: {e}")
        return False
    finally:
        cleanup()

def run_short_video_workflow(animal: str, schedule_time: datetime):
    """
    الخطوات الكاملة لإنشاء ورفع فيديو قصير
    """
    print(f"\n--- 🎶 STARTING SHORT VIDEO WORKFLOW: {animal} ---")
    try:
        # 1. إنشاء الـ SEO
        metadata = ai_content.generate_short_video_idea(animal)
        
        # 2. جلب الموسيقى
        music_file = audio_generation.get_copyright_free_music()
        if not music_file:
            raise Exception("Shorts require music! Download failed.")
            
        # 3. تجميع الفيديو
        video_path = video_assembly.assemble_short_video(animal, music_file)
        
        # 4. رفع الفيديو
        youtube_uploader.schedule_video_upload(
            video_path, metadata, schedule_time, is_short=True
        )
        
        print(f"--- ✅ SHORT VIDEO WORKFLOW SUCCESS: {animal} ---")
        return True

    except Exception as e:
        print(f"--- ❌ SHORT VIDEO WORKFLOW FAILED: {animal} ---")
        print(f"Error: {e}")
        return False
    finally:
        cleanup()

def main():
    """
    الـ "مايسترو" الرئيسي
    """
    start_time = datetime.now()
    print(f"--- YouTube Content Factory Started at {start_time} ---")
    
    # بنشوف إذا كان ده "Test Run" من GitHub Actions
    is_test_run = os.getenv('IS_TEST_RUN', 'false').lower() == 'true'
    
    if is_test_run:
        print("🚀 !!! RUNNING IN TEST MODE !!! 🚀")
        print("Will generate and upload 1 video immediately.")
        
        used_animals = state_manager.get_used_animals()
        animal = ai_content.get_animal_ideas(used_animals, 1)[0]
        
        # (Req #4): فيديو واحد تجريبي
        run_long_video_workflow(animal, "male", schedule_time=None) # None = publish now
        
        # بنسجل الحيوان عشان مانستخدموش بكرة
        state_manager.add_used_animals([animal])
        
    else:
        print("🗓️ --- RUNNING IN SCHEDULED MODE --- 🗓️")
        
        # 1. هات الأفكار
        used_animals = state_manager.get_used_animals()
        # (2 طويل + 5 قصير)
        new_animals = ai_content.get_animal_ideas(used_animals, 7)
        
        if len(new_animals) < 7:
            print("Error: OpenAI did not return enough new animals.")
            return

        animals_long = new_animals[0:2]
        animals_shorts = new_animals[2:7]
        
        # 2. تنفيذ الـ Pipeline
        # (الجدولة متظبطة في SCHEDULE_TIMES_UTC)
        
        run_short_video_workflow(animals_shorts[0], get_schedule_time(0))
        run_long_video_workflow(animals_long[0], "male", get_schedule_time(1))
        run_short_video_workflow(animals_shorts[1], get_schedule_time(2))
        run_short_video_workflow(animals_shorts[2], get_schedule_time(3))
        run_long_video_workflow(animals_long[1], "female", get_schedule_time(4)) # تبديل الصوت
        run_short_video_workflow(animals_shorts[3], get_schedule_time(5))
        run_short_video_workflow(animals_shorts[4], get_schedule_time(6))

        # 3. تسجيل كل الحيوانات اللي استخدمناها
        state_manager.add_used_animals(new_animals)

    end_time = datetime.now()
    print(f"--- Workflow Finished at {end_time}. Duration: {end_time - start_time} ---")

if __name__ == "__main__":
    main()
