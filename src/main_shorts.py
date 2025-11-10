import os
import random
import datetime
import json
from youtube import upload_video
from media_sources import pick_video_urls
from music_picker import pick_music

def main():
    print("🎬 Starting shorts automation...")
    os.makedirs("output", exist_ok=True)

    # تحميل الحيوانات التريند
    animals = []
    if os.path.exists("data/trending_animals.json"):
        with open("data/trending_animals.json", "r", encoding="utf-8") as f:
            animals = json.load(f)
    if not animals:
        animals = ["Lion", "Elephant", "Tiger", "Panda", "Shark", "Giraffe"]

    # ✅ أول شورت ينزل فوراً
    animal = random.choice(animals)
    print(f"🎞️ Selected animal: {animal}")
    video_urls = pick_video_urls(animal)
    music = pick_music()
    short_file = video_urls[0]  # أول فيديو قصير

    title = f"{animal} in Action! 🐾 #Shorts"
    desc = f"Watch this amazing {animal}! Subscribe for more wild videos! 🌿"
    tags = ["shorts", "wildlife", "animals", animal.lower()]

    print("🚀 Uploading first short now...")
    upload_video(short_file, title, desc, tags, privacy="public")

    # ✅ باقي الشورتات المجدولة
    times = ["10:00", "14:00", "18:00", "22:00"]  # أفضل أوقات للجمهور الأجنبي
    now = datetime.datetime.utcnow()
    for t in times:
        hour, minute = map(int, t.split(":"))
        schedule_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if schedule_time < now:
            schedule_time += datetime.timedelta(days=1)
        schedule_time_iso = schedule_time.isoformat() + "Z"
        print(f"🕒 Scheduling short for {schedule_time_iso}")
        upload_video(short_file, title, desc, tags, privacy="private", schedule_time_rfc3339=schedule_time_iso)

if __name__ == "__main__":
    main()
