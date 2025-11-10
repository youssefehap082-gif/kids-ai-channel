import sys, os, random, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.media_sources import pick_video_urls
from src.compose import compose_video
from src.tts import synthesize
from src.youtube import upload_video
from src.text_overlay import generate_subtitles
from src.utils import get_animal_facts

# 🔥 إعداد عام
ANIMALS = ["lion", "elephant", "giraffe", "panda", "tiger", "dolphin", "zebra", "eagle", "turtle", "wolf"]

def main():
    try:
        # ✅ اختار حيوان عشوائي بدون تكرار
        animal = random.choice(ANIMALS)
        print(f"🎬 Generating video for: {animal}")

        # ✅ اجمع فيديوهات من Pixabay / Pexels / Storyblocks / Vecteezy
        urls = pick_video_urls(animal, need=10, prefer_vertical=False)
        
        # ✅ أنشئ نص المعلومات
        facts = get_animal_facts(animal)
        voice_path = synthesize(facts, voice_type=random.choice(["male", "female"]))
        
        # ✅ أنشئ الترجمة النصية المتزامنة
        subtitle_path = generate_subtitles(facts)
        
        # ✅ أنشئ الفيديو النهائي
        final_path = compose_video(urls, voice_path, subtitle_path, min_duration=185)
        
        # ✅ ارفع الفيديو مباشرة بدون جدولة
        title = f"10 Amazing Facts About the {animal.title()} You Didn’t Know!"
        desc = f"Discover 10 fascinating facts about the {animal.title()}!\n#Wildlife #Animals #Nature"
        tags = [animal, "wildlife", "animals", "nature", "facts"]
        
        upload_video(final_path, title, desc, tags, privacy="public", schedule_time_rfc3339=None)
        print("✅ Video uploaded successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
