import sys, os, random
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.media_sources import pick_video_urls
from src.compose import compose_short
from src.youtube import upload_video
from src.music import get_background_music
from src.optimizer_ai import recommend_next_animals, record_video_result

def main():
    try:
        # 🧠 احصل على الحيوانات الموصى بها من الذكاء الاصطناعي
        _, short_animals = recommend_next_animals(n_long=4, n_short=8)
        print(f"🤖 AI suggested shorts for today: {short_animals}")

        # 🔁 إنتاج 8 شورتس تلقائيًا
        for animal in short_animals:
            print(f"🎬 Generating short for: {animal}")
            urls = pick_video_urls(animal, need=4, prefer_vertical=True)
            music_path = get_background_music()
            final_path = compose_short(urls, music_path, target_duration=58)

            # ✅ عنوان بسيط وسهل النشر
            title = f"{animal.title()} — Stunning Wildlife Moment! 🐾 #Shorts"
            desc = f"Beautiful footage of the {animal.title()} in nature! 🐾\n#Animals #Wildlife #Nature"
            tags = [animal, "wildlife", "animals", "shorts"]

            vid = upload_video(final_path, title, desc, tags, privacy="public", schedule_time_rfc3339=None)
            record_video_result(vid, title, is_short=True)

            print(f"✅ Uploaded short for {animal}")

    except Exception as e:
        print(f"❌ Error in shorts: {e}")

if __name__ == "__main__":
    main()
