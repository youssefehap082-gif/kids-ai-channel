import sys, os, random, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.media_sources import pick_video_urls
from src.compose import compose_video
from src.tts import synthesize
from src.youtube import upload_video
from src.text_overlay import generate_subtitles, add_text_overlay, translate_text
from src.utils import get_animal_facts
from src.optimizer_ai import recommend_next_animals, record_video_result
from moviepy.editor import VideoFileClip

def main():
    try:
        # 🧠 احصل على الحيوانات الموصى بها من الذكاء الاصطناعي
        long_animals, _ = recommend_next_animals(n_long=4, n_short=8)
        print(f"🤖 AI suggested animals for today: {long_animals}")

        # 🔁 إنتاج 4 فيديوهات طويلة في اليوم
        for animal in long_animals:
            print(f"🎬 Generating video for: {animal}")

            # ✅ جمع الفيديوهات والصوت والمعلومات
            urls = pick_video_urls(animal, need=10, prefer_vertical=False)
            facts = get_animal_facts(animal)
            voice_path = synthesize(facts, voice_type=random.choice(["male", "female"]))
            subtitle_path = generate_subtitles(facts)

            # ✅ إنشاء الفيديو
            final_path = compose_video(urls, voice_path, subtitle_path, min_duration=200)
            video = VideoFileClip(final_path)

            # ✅ النصوص على الشاشة + الترجمة بلغات تانية
            video_with_text = add_text_overlay(video, facts)
            overlay_path = f"/tmp/{animal}_overlay.mp4"
            video_with_text.write_videofile(overlay_path, codec="libx264", audio_codec="aac")

            translations = translate_text(facts)
            for lang, translated in translations.items():
                generate_subtitles(translated, lang)
                print(f"🌍 Added subtitles for {lang}")

            # ✅ العنوان والوصف
            title = f"10 Amazing Facts About the {animal.title()} You Didn’t Know!"
            desc = f"Discover fascinating facts about the {animal.title()} and other wildlife.\n#Wildlife #Nature #Animals #Facts"
            tags = [animal, "wildlife", "nature", "animals", "facts"]

            # ✅ الرفع
            vid = upload_video(overlay_path, title, desc, tags, privacy="public", schedule_time_rfc3339=None)
            record_video_result(vid, title, is_short=False)

            print(f"✅ Uploaded long video for {animal}")

    except Exception as e:
        print(f"❌ Error in long videos: {e}")

if __name__ == "__main__":
    main()
