import sys, os, random
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.media_sources import pick_video_urls
from src.compose import compose_short
from src.youtube import upload_video
from src.music import get_background_music

ANIMALS = ["lion", "elephant", "panda", "turtle", "tiger", "fox", "owl", "eagle", "giraffe", "koala", "wolf", "crocodile"]

def main():
    try:
        animal = random.choice(ANIMALS)
        print(f"🎬 Generating short for: {animal}")

        urls = pick_video_urls(animal, need=4, prefer_vertical=True)
        music_path = get_background_music()
        final_path = compose_short(urls, music_path, target_duration=58)

        # ✅ عنوان SEO بسيط ومؤثر
        title = f"{animal.title()} — Epic Wild Moment! 🐾 #Shorts"
        desc = f"Stunning footage of the {animal.title()} in the wild. #Animals #Wildlife #Nature"
        tags = [animal, "wildlife", "animals", "shorts", "nature"]

        upload_video(final_path, title, desc, tags, privacy="public", schedule_time_rfc3339=None)
        print("✅ Short uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
