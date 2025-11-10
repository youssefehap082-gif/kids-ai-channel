import os
import random
import datetime
import json
from youtube import upload_video
from compose import compose_video
from media_sources import pick_video_urls
from tts import synthesize

# ✅ تشغيل فيديو واحد مباشر والباقي متأخر حسب الجدول
def main():
    print("🎬 Starting long video automation...")
    os.makedirs("output", exist_ok=True)

    # اختيار الحيوانات التريند
    animals = []
    if os.path.exists("data/trending_animals.json"):
        with open("data/trending_animals.json", "r", encoding="utf-8") as f:
            animals = json.load(f)
    if not animals:
        animals = ["Lion", "Elephant", "Tiger", "Panda", "Cheetah", "Shark"]

    # ✅ اختار أول حيوان للفيديو الفوري
    animal = random.choice(animals)
    print(f"🐾 Selected animal: {animal}")

    # توليد الفيديو
    video_paths = pick_video_urls(animal)
    voice_path = synthesize(animal, "facts about the " + animal)
    final = compose_video(video_paths, voice_path)

    # رفع أول فيديو فوراً
    title = f"{animal} — Mind-Blowing Facts! 🐾"
    desc = f"Discover amazing facts about the {animal}. Subscribe for more daily wild content! 🌍"
    tags = ["wildlife", "animals", "nature", animal.lower()]

    print("🚀 Uploading first long video now...")
    upload_video(str(final), title, desc, tags, privacy="public")

    # ✅ تحديد باقي الفيديوهات للأوقات المثالية
    times = ["11:00", "15:00", "20:00"]  # بتوقيت GMT
    now = datetime.datetime.utcnow()
    for t in times:
        hour, minute = map(int, t.split(":"))
        schedule_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if schedule_time < now:
            schedule_time += datetime.timedelta(days=1)
        schedule_time_iso = schedule_time.isoformat() + "Z"
        print(f"🕒 Scheduling next long video for {schedule_time_iso}")
        upload_video(str(final), title, desc, tags, privacy="private", schedule_time_rfc3339=schedule_time_iso)

if __name__ == "__main__":
    main()
