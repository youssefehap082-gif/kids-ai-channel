import os, random, time
from src.media_sources import pick_video_urls
from src.compose import compose_short
from src.youtube import upload_video
from src.utils import generate_thumbnail_ai, generate_hashtags

def main():
    print("🎞 Generating AI Animal Shorts...")

    animals = ["Lion", "Panda", "Koala", "Eagle", "Crocodile", "Elephant", "Shark", "Tiger", "Owl", "Cheetah"]
    random.shuffle(animals)

    for idx, animal in enumerate(animals[:6]):
        try:
            print(f"🐾 Creating short for {animal}")
            urls = pick_video_urls(animal, need=6, prefer_vertical=True)
            short_path = compose_short(urls, target_duration=58)

            thumb = generate_thumbnail_ai(animal)
            hashtags = generate_hashtags(animal)
            title = f"The {animal} in Action 🐾 #Shorts"
            desc = f"Watch the {animal} in its natural beauty! 🐾\n{hashtags}"

            upload_video(short_path, title, desc, [animal, "shorts", "wildlife"], thumb_path=thumb, privacy="public")
            print(f"✅ Uploaded short for {animal}")
            time.sleep(10)
        except Exception as e:
            print(f"⚠️ Error with {animal}: {e}")

    print("🎯 All shorts uploaded successfully!")

if __name__ == "__main__":
    main()
