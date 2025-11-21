import os
import sys
import json
import random

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media, download_video
from voice_engine import generate_voice
from editor_engine import create_video
from uploader_engine import upload_video

def get_random_animal():
    # بنحاول نقرأ من ملف القائمة
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'animals_list.json')
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        # نختار فئة عشوائية (مثلاً cute أو predators)
        categories = list(data['categories'].keys())
        random_cat = random.choice(categories)
        
        # نختار حيوان عشوائي من الفئة دي
        animal = random.choice(data['categories'][random_cat])
        print(f"🎲 Selected Random Animal: {animal} (Category: {random_cat})")
        return animal
    except Exception as e:
        print(f"⚠️ Could not read list, defaulting to Lion. Error: {e}")
        return "Lion"

def run_pipeline():
    print("🏁 Starting DAILY AUTO-TUBE Pipeline...")
    
    # 1. Topic (الاختيار العشوائي)
    animal = get_random_animal()
    
    # 2. Script
    script_data = generate_script(animal)
    
    # 3. Voice
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: sys.exit(1)

    # 4. Media
    video_urls = gather_media(animal)
    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    
    if not video_urls:
        print("❌ No videos found on Pexels!")
        sys.exit(1)

    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        try:
            download_video(url, path)
            local_videos.append(path)
        except:
            pass
    
    if not local_videos: 
        print("❌ Failed to download any videos.")
        sys.exit(1)

    # 5. Edit
    final_video = create_video(local_videos, audio_path)
    if not final_video: 
        print("❌ Editing Failed.")
        sys.exit(1)

    # 6. Upload
    video_id = upload_video(final_video, script_data['title'], script_data['description'])
    
    if not video_id:
        print("❌ Upload return no ID. Failing pipeline.")
        sys.exit(1)
    
    print(f"🎉🎉🎉 SUCCESS! Video about {animal} is LIVE!")

if __name__ == "__main__":
    run_pipeline()
