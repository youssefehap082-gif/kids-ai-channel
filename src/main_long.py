import sys, os, random, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.media_sources import pick_video_urls
from src.compose import compose_video
from src.tts import synthesize
from src.youtube import upload_video
from src.text_overlay import generate_subtitles, add_text_overlay, translate_text
from src.utils import get_animal_facts
from moviepy.editor import VideoFileClip

ANIMALS = ["lion", "elephant", "tiger", "giraffe", "panda", "dolphin", "zebra", "owl", "fox", "bear", "kangaroo", "eagle", "penguin", "wolf"]

def main():
    try:
        animal = random.choice(ANIMALS)
        print(f"🎬 Generating video for: {animal}")

        # ✅ اجلب الفيديوهات
        urls = pick_video_urls(animal, need=10, prefer_vertical=False)
        facts = get_animal_facts(animal)

        # ✅ صوت + ترجمة
        voice_path = synthesize(facts, voice_type=random.choice(["male", "female"]))
        subtitle_path = generate_subtitles(facts)

        # ✅ الفيديو الأساسي
        final_path = compose_video(urls, voice_path, subtitle_path, min_duration=200)
        video = VideoFileClip(final_path)

        # ✅ أضف النص على الشاشة
        video_with_text = add_text_overlay(video, facts)
        video_with_text.write_videofile("/tmp/final_overlay.mp4", codec="libx264", audio_codec="aac")

        # ✅ ترجمات بلغات أخرى
        translations = translate_text(facts)
        for lang, translated in translations.items():
            srt_path = generate_subtitles(translated, lang)
            print(f"🌍 Added subtitles for {lang}")

        # ✅ إعداد SEO وعنوان ووصف
        title = f"10 Amazing Facts About the {animal.title()} You Didn’t Know!"
        desc = f"Discover incredible facts about the {animal.title()} and other wildlife.\n#Wildlife #Nature #Animals #Facts"
        tags = [animal, "wildlife", "nature", "animals", "facts"]

        # ✅ رفع الفيديو
        upload_video("/tmp/final_overlay.mp4", title, desc, tags, privacy="public", schedule_time_rfc3339=None)
        print("✅ Video uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
