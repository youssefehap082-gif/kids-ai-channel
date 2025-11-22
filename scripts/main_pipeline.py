import os
import sys
import random
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media, download_video, get_thumbnail_image
from voice_engine import generate_voice
from editor_engine import create_video, create_thumbnail
from uploader_engine import upload_video

def get_random_animal():
    # قائمة متنوعة جداً
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
    
    animal = get_random_animal()
    print(f"🦁 Subject: {animal}")
    
    # 1. Script
    try:
        script_data = generate_script(animal, mode=mode)
    except Exception as e:
        print(f"❌ Script Failed: {e}")
        return

    # 2. Voice
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: return

    # 3. Music
    local_music = "background.mp3"
    music_path = local_music if os.path.exists(local_music) else None

    # 4. Media
    orientation = "landscape" if mode == "long" else "portrait"
    # لو طويل هات 12 فيديو عشان يغطي الـ 10 حقائق
    limit = 12 if mode == "long" else 5 
    
    video_urls = gather_media(animal, orientation=orientation, limit=limit)
    if not video_urls: return

    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        try:
            download_video(url, path)
            local_videos.append(path)
        except: pass
    
    if len(local_videos) < 2:
        print("❌ Not enough videos downloaded!")
        return

    # 5. Edit
    final_video = create_video(local_videos, audio_path, music_path, mode=mode)
    if not final_video: return

    # 6. Thumbnail (Long Only)
    thumb_path = None
    if mode == "long":
        raw_thumb = get_thumbnail_image(animal)
        if raw_thumb:
            thumb_path = create_thumbnail(raw_thumb, f"{animal} FACTS")

    # 7. Upload
    video_id = upload_video(
        final_video, 
        script_data['title'], 
        script_data['description'], 
        script_data['tags'],
        thumb_path
    )
    
    if video_id:
        print(f"✅ SUCCESS! {mode} video live: https://youtu.be/{video_id}")

if __name__ == "__main__":
    # تشغيل الشورتس ثم الطويل
    print("🧪 FULL TEST: Generating 1 SHORT & 1 LONG (10 Facts)...")
    
    print("\n--- STEP 1: SHORTS ---")
    execute_run("short")
    
    print("\n--- STEP 2: LONG VIDEO ---")
    execute_run("long")
