# المسار: src/main.py

import os
import shutil
from datetime import datetime, timedelta

from src import ai_content, audio_generation, video_assembly, youtube_uploader, state_manager
from src.config import ASSETS_DIR

# --- إعدادات الجدولة الجديدة (6 فيديوهات) ---
SCHEDULE_TIMES_UTC = [
    13, # 1 PM UTC - Short 1
    15, # 3 PM UTC - Long Video 1
    17, # 5 PM UTC - Short 2
    19, # 7 PM UTC - Short 3
    21, # 9 PM UTC - Long Video 2
    23  # 11 PM UTC - Short 4
]

def get_schedule_time(index: int) -> datetime:
    """
    يحسب ميعاد النشر بتوقيت UTC
    """
    now = datetime.utcnow()
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

def run_long_video_workflow(animal: str, schedule_time: datetime):
    """
    الخطوات الكاملة لإنشاء ورفع فيديو طويل (بدون تبديل صوت وبدون ترجمة)
    """
    print(f"\n--- 🎬 STARTING LONG VIDEO WORKFLOW (FREE): {animal} ---")
    try:
        # 1. إنشاء السكريبت و الـ SEO (مجاني)
        metadata = ai_content.generate_long_video_script(animal)
        facts = metadata['facts']
        
        # 2. إنشاء التعليق الصوتي (مجاني - صوت واحد)
        vo_files, vo_durations = audio_generation.generate_all_vo_files(facts)
        
        # 3. جلب الموسيقى (مجاني)
        music_file = audio_generation.get_copyright_free_music()
        
        # 4. تجميع الفيديو
        video_path = video_assembly.assemble_long_video(
            animal, facts, vo_files, vo_durations, music_file
        )
        
        # 5. رفع الفيديو (بدون ترجمة)
        video_id = youtube_uploader.schedule_video_upload(
            video_path, metadata, schedule_time, is_short=False
        )
        
        if not video_id:
            raise Exception("Video upload failed.")
            
        # 6. قسم الترجمة (SRT) تم حذفه
        
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
        # 1. إنشاء الـ SEO (مجاني)
        metadata = ai_content.generate_short_video_idea(animal)
        
        # 2. جلب الموسيقى (مجاني)
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
    print(f"--- YouTube Content Factory (FREE VERSION) Started at {start_time} ---")
    
    is_test_run = os.getenv('IS_TEST_RUN', 'false').lower() == 'true'
    
    if is_test_run:
        print("🚀 !!! RUNNING IN TEST MODE !!! 🚀")
        used_animals = state_manager.get_used_animals()
        animal = ai_content.get_animal_ideas(used_animals, 1)[0]
        
        run_long_video_workflow(animal, schedule_time=None) # Publish now
        
        state_manager.add_used_animals([animal])
        
    else:
        print("🗓️ --- RUNNING IN SCHEDULED MODE --- 🗓️")
        
        # 1. هات الأفكار (2 طويل + 4 قصير = 6)
        used_animals = state_manager.get_used_animals()
        new_animals = ai_content.get_animal_ideas(used_animals, 6)
        
        if len(new_animals) < 6:
            print("Error: OpenAI did not return enough new animals.")
            return

        animals_long = new_animals[0:2]
        animals_shorts = new_animals[2:6]
        
        # 2. تنفيذ الـ Pipeline (بالجدول الجديد)
        run_short_video_workflow(animals_shorts[0], get_schedule_time(0))
        run_long_video_workflow(animals_long[0], get_schedule_time(1))
        run_short_video_workflow(animals_shorts[1], get_schedule_time(2))
        run_short_video_workflow(animals_shorts[2], get_schedule_time(3))
        run_long_video_workflow(animals_long[1], get_schedule_time(4)) # (نفس الصوت)
        run_short_video_workflow(animals_shorts[3], get_schedule_time(5))

        # 3. تسجيل كل الحيوانات اللي استخدمناها
        state_manager.add_used_animals(new_animals)

    end_time = datetime.now()
    print(f"--- Workflow Finished at {end_time}. Duration: {end_time - start_time} ---")

if __name__ == "__main__":
    main()
