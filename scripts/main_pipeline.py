import os
import sys
import random
import json
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media, download_video, get_thumbnail_image
from voice_engine import generate_voice
from editor_engine import create_video, create_thumbnail
from uploader_engine import upload_video

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
    print(f"\n{'='*30}\n🚀 STARTING PIPELINE: {mode.upper()}\n{'='*30}")
    
    try:
        animal = get_random_animal()
        print(f"🦁 Subject: {animal}")
        
        # 1. Script
        script_data = generate_script(animal, mode=mode)
        
        # 2. Voice
        audio_path = generate_voice(script_data['script_text'])
        if not audio_path: raise Exception("Voice failed")

        # 3. Music
        local_music = "background.mp3"
        music_path = local_music if os.path.exists(local_music) else None

        # 4. Media
        orientation = "landscape" if mode == "long" else "portrait"
        limit = 20 if mode == "long" else 5 # بنطلب 20 فيديو عشان نغطي الـ 3 دقايق
        
        video_urls = gather_media(animal, orientation=orientation, limit=limit)
        if not video_urls: raise Exception("No media found")

        local_videos = []
        os.makedirs("assets/temp", exist_ok=True)
        for i, url in enumerate(video_urls):
            path = f"assets/temp/clip_{i}.mp4"
            try:
                download_video(url, path)
                local_videos.append(path)
            except: pass
        
        if len(local_videos) < 2: raise Exception("Downloads failed")

        # 5. Edit
        final_video = create_video(local_videos, audio_path, music_path, mode=mode)
        if not final_video: raise Exception("Editing failed")

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
        else:
            print("❌ Upload failed (No ID returned)")

    except Exception as e:
        print(f"❌ PIPELINE FAILED for {mode}:")
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 DUAL TEST MODE: Running Short THEN Long...")
    
    # نشغل الشورتس الأول
    execute_run("short")
    
    print("\n⏳ Waiting 10 seconds before Long video...")
    import time
    time.sleep(10)
    
    # نشغل الطويل
    execute_run("long")
    
