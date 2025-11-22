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
    # القائمة المدمجة لمنع التكرار
    animals = [
        "Jaguar", "Polar Bear", "Komodo Dragon", "Great White Shark", "Saltwater Crocodile", 
        "Gray Wolf", "Cheetah", "Grizzly Bear", "Red Panda", "Quokka", "Sea Otter", 
        "Capybara", "Fennec Fox", "Koala", "Sloth", "Meerkat", "Emperor Penguin", 
        "Blue Whale", "Mantis Shrimp", "Orca", "Hammerhead Shark", "Shoebill Stork", 
        "Peregrine Falcon", "Snowy Owl", "Eagle", "Toucan", "Praying Mantis", 
        "Hercules Beetle", "Platypus", "Axolotl", "Pangolin", "Honey Badger"
    ]
    # اختيار عشوائي
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
        print(f"❌ Script Error: {e}")
        sys.exit(1)
    
    # 2. Voice
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: sys.exit(1)

    # 3. Music
    local_music = "background.mp3"
    music_path = local_music if os.path.exists(local_music) else None
    if not music_path: print("⚠️ WARNING: No background.mp3 found!")

    # 4. Media
    orientation = "landscape" if mode == "long" else "portrait"
    video_urls = gather_media(animal, orientation=orientation)
    
    if not video_urls: 
        print("❌ No videos found!")
        sys.exit(1)

    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    
    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        try:
            download_video(url, path)
            local_videos.append(path)
        except: pass
    
    if not local_videos: 
        print("❌ No videos downloaded")
        sys.exit(1)

    # 5. Edit
    print("🎬 Starting Editing...")
    final_video = create_video(local_videos, audio_path, music_path, mode=mode)
    
    if not final_video: 
        print("❌ EDITING FAILED.")
        sys.exit(1)

    # 6. Thumbnail (Long Only)
    thumb_path = None
    if mode == "long":
        print("🖼️ Generating Thumbnail...")
        raw_thumb = get_thumbnail_image(animal)
        if raw_thumb:
            thumb_path = create_thumbnail(raw_thumb, f"{animal} FACTS")

    # 7. Upload
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
        print("❌ Upload Failed")
        sys.exit(1)

if __name__ == "__main__":
    print("🧪 TEST MODE: Generating 1 LONG Video Only...")
    execute_run("long")
