import os
import sys
import random
import datetime

# إضافة المسار عشان يشوف باقي الملفات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media, download_video, get_thumbnail_image
from voice_engine import generate_voice
from editor_engine import create_video, create_thumbnail
from uploader_engine import upload_video

# --- التعديل الأول: القائمة جوه الكود عشان نضمن التنوع ---
def get_random_animal():
    animals = [
        "Jaguar", "Polar Bear", "Komodo Dragon", "Great White Shark", "Saltwater Crocodile", 
        "Gray Wolf", "Cheetah", "Grizzly Bear", "Red Panda", "Quokka", "Sea Otter", 
        "Capybara", "Fennec Fox", "Koala", "Sloth", "Meerkat", "Emperor Penguin", 
        "Blue Whale", "Mantis Shrimp", "Orca", "Hammerhead Shark", "Shoebill Stork", 
        "Peregrine Falcon", "Snowy Owl", "Eagle", "Toucan", "Praying Mantis", 
        "Hercules Beetle", "Platypus", "Axolotl", "Pangolin", "Honey Badger"
    ]
    selected = random.choice(animals)
    print(f"🎲 System Selected: {selected}")
    return selected

def execute_run(mode):
    print(f"\n🚀 STARTING PIPELINE: {mode.upper()} MODE")
    
    # 1. اختيار حيوان (مختلف كل مرة)
    animal = get_random_animal()
    print(f"🦁 Subject: {animal}")
    
    # 2. كتابة السكريبت
    try:
        script_data = generate_script(animal, mode=mode)
    except Exception as e:
        print(f"❌ Script Error: {e}")
        return

    # 3. الصوت
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: 
        print("❌ Voice Failed")
        return

    # 4. الموسيقى
    local_music = "background.mp3"
    music_path = local_music if os.path.exists(local_music) else None
    if not music_path: print("⚠️ WARNING: No background.mp3 found!")

    # 5. تجميع الفيديوهات
    orientation = "landscape" if mode == "long" else "portrait"
    video_urls = gather_media(animal, orientation=orientation)
    
    if not video_urls: 
        print("❌ No videos found!")
        return

    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    
    print("📥 Downloading clips...")
    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        try:
            download_video(url, path)
            local_videos.append(path)
        except: pass
    
    if not local_videos: return

    # 6. المونتاج (المرحلة الصعبة)
    print("🎬 Editing started...")
    final_video = create_video(local_videos, audio_path, music_path, mode=mode)
    if not final_video: 
        print("❌ Editing Failed (Likely Memory Issue).")
        return

    # 7. الثامبنيل (للطويل فقط)
    thumb_path = None
    if mode == "long":
        print("🖼️ Generating Thumbnail...")
        raw_thumb = get_thumbnail_image(animal)
        if raw_thumb:
            thumb_path = create_thumbnail(raw_thumb, f"{animal} FACTS")

    # 8. الرفع
    print("🚀 Uploading...")
    video_id = upload_video(
        final_video, 
        script_data['title'], 
        script_data['description'], 
        script_data['tags'],
        thumb_path
    )
    
    if video_id:
        print(f"✅ SUCCESS! {mode} video live: https://youtu.be/{video_id}")
    else:
        print("❌ Upload Failed.")

if __name__ == "__main__":
    # --- التعديل الثاني: تشغيل واحد فقط عشوائي أو حسب الوقت ---
    # عشان الرامات متفرقعش، هنقرر هنعمل إيه ونعمل واحد بس
    
    # لو عايز تجرب دلوقتي حالا (Test)، هنخليه يعمل LONG بس عشان نتأكد منه
    # بعد ما نتأكد، هنرجع الكود ده للأوتوماتيك
    
    print("🧪 FORCED TEST: Attempting LONG VIDEO Only (to fix the issue)")
    execute_run("long")
