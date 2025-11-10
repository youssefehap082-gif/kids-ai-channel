import sys, os, random
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.media_sources import pick_video_urls
from src.compose import compose_short
from src.youtube import upload_video
from src.music import get_background_music

# 🔥 إعداد عام
ANIMALS = ["lion", "elephant", "panda", "turtle", "tiger", "fox", "owl", "eagle", "giraffe", "koala"]

def main():
    try:
        animal = random.choice(ANIMALS)
        print(f"🎬 Generating short for: {animal}")

        # ✅ احصل على فيديوهات رأسية
        urls = pick_video_urls(animal, need=4, prefer_vertical=True)
        
        # ✅ احصل على موسيقى مجانية بدون حقوق
        music_path = get_background_music()
        
        # ✅ أنشئ الفيديو القصير
        final_path = compose_short(urls, music_path, target_duration=58)
        
        # ✅ عنوان بسيط للشورت
        title = f"{animal.title()} — Mind-Blowing Fact! #Shorts"
        desc = f"Enjoy amazing wildlife footage of the {animal.title()}! 🐾\n#Animals #Wildlife #Nature"
        tags = [animal, "wildlife", "animals", "shorts"]
        
        upload_video(final_path, title, desc, tags, privacy="public", schedule_time_rfc3339=None)
        print("✅ Short uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
