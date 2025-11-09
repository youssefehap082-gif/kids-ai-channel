import os, random, time
from src.media_sources import pick_video_urls
from src.compose import compose_short
from src.youtube import upload_video

def main():
    print("🎞 Generating Animal Shorts...")

    animals = ["Lion", "Elephant", "Panda", "Tiger", "Zebra", "Giraffe", "Kangaroo", "Koala", "Penguin", "Crocodile"]
    random.shuffle(animals)

    for idx, animal in enumerate(animals[:6]):
        print(f"🎬 Creating short for {animal}")

        # 1. جلب الفيديوهات (موسيقى فقط)
        urls = pick_video_urls(animal, need=6, prefer_vertical=True)

        # 2. دمج الفيديوهات + موسيقى خلفية
        short_video = compose_short(urls, target_duration=58)

        # 3. تجهيز العنوان والوصف
        title = f"The {animal} in Action 🐾 #Shorts"
        desc = f"Watch this amazing {animal} moment! 🐾\n#Nature #Wildlife #Animals"
        tags = [animal, "shorts", "wildlife", "nature"]

        # 4. رفع الفيديو
        upload_video(short_video, title, desc, tags, privacy="public")

        print(f"✅ Uploaded short for {animal}")
        time.sleep(10)

if __name__ == "__main__":
    main()
