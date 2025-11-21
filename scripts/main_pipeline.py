import os
import sys
import json
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
# شيلنا get_background_music عشان هنستخدم ملفك المحلي
from media_engine import gather_media, download_video
from voice_engine import generate_voice
from editor_engine import create_video
from uploader_engine import upload_video

def get_random_animal():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'animals_list.json')
        with open(config_path, 'r') as f:
            data = json.load(f)
        categories = list(data['categories'].keys())
        random_cat = random.choice(categories)
        animal = random.choice(data['categories'][random_cat])
        print(f"🎲 Selected Random Animal: {animal}")
        return animal
    except:
        return "Lion"

def run_pipeline():
    print("🏁 Starting FULL AUTO Pipeline...")
    
    animal = get_random_animal()
    script_data = generate_script(animal)
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: sys.exit(1)

    # --- التعديل هنا: استخدام الموسيقى بتاعتك ---
    # بندور على الملف في الفولدر الرئيسي
    local_music = "background.mp3" 
    music_path = None
    
    if os.path.exists(local_music):
        print("🎵 Found local background.mp3, using it.")
        music_path = local_music
    else:
        print("⚠️ No local music found. Video will have voice only.")
    # ---------------------------------------------

    video_urls = gather_media(animal)
    if not video_urls: sys.exit(1)

    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        try:
            download_video(url, path)
            local_videos.append(path)
        except: pass
    
    if not local_videos: sys.exit(1)

    # بنبعت الموسيقى للمونتاج
    final_video = create_video(local_videos, audio_path, music_path)
    if not final_video: sys.exit(1)

    video_id = upload_video(final_video, script_data['title'], script_data['description'])
    if not video_id: sys.exit(1)
    
    print(f"🎉 SUCCESS! Video Live: https://youtu.be/{video_id}")

if __name__ == "__main__":
    run_pipeline()
