import os, random, time, csv
from datetime import datetime
from src.media_sources import pick_video_urls
from src.tts import generate_tts
from src.compose import compose_video
from src.youtube import upload_video, get_video_stats
from src.subtitles import add_subtitles
from src.utils import get_animal_facts, get_trending_animals, generate_hashtags, generate_thumbnail_ai
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips

def main():
    print("🐾 Starting WildFacts AI System...")

    # ✅ جلب الحيوانات الأكثر بحثًا الأسبوع الحالي
    animals = get_trending_animals()
    if not animals:
        animals = ["Lion", "Elephant", "Tiger", "Panda", "Cheetah", "Shark", "Koala"]

    random.shuffle(animals)

    for idx, animal in enumerate(animals[:3]):
        try:
            print(f"🎬 Generating video for: {animal}")

            # 1️⃣ جلب حقائق الحيوان
            facts = get_animal_facts(animal)
            script_text = " ".join(facts)

            # 2️⃣ توليد التعليق الصوتي + صوت ختام
            voice_file = generate_tts(script_text, voice="Rachel")
            outro_voice = generate_tts("Subscribe for more amazing animal facts!", voice="Rachel")

            # 3️⃣ جلب الفيديوهات
            urls = pick_video_urls(animal, need=10, prefer_vertical=False)
            main_video = compose_video(urls, voice_file, min_duration=180)

            # 4️⃣ إضافة الترجمة النصية المتزامنة
            subtitled_video = add_subtitles(main_video, script_text)

            # 5️⃣ إضافة Outro بلوجو القناة + الصوت الختامي
            logo_path = "assets/logo.png"
            outro_img = ImageClip(logo_path).set_duration(4).resize(height=250).set_position(("center", "center"))
            outro_clip = CompositeVideoClip([outro_img.fadein(1).fadeout(1)])
            outro_clip.audio = VideoFileClip(outro_voice).audio
            base_clip = VideoFileClip(subtitled_video)
            final_clip = concatenate_videoclips([base_clip, outro_clip])
            final_path = f"/tmp/{animal.lower()}_final.mp4"
            final_clip.write_videofile(final_path, codec="libx264", audio_codec="aac")

            # 6️⃣ توليد كفر AI
            thumb_path = generate_thumbnail_ai(animal)

            # 7️⃣ توليد الهاشتاجات
            hashtags = generate_hashtags(animal)
            desc = f"Discover 10 fascinating facts about the {animal}! 🐾\n\n{hashtags}\nSubscribe for more!"

            # 8️⃣ رفع الفيديو
            title = f"10 Amazing Facts About the {animal} You Didn't Know!"
            tags = [animal, "Wildlife", "Animals", "Nature"]
            video_id = upload_video(final_path, title, desc, tags, thumb_path=thumb_path, privacy="public")
            print(f"✅ Uploaded {animal}: https://youtu.be/{video_id}")

            # 9️⃣ تسجيل الإحصائيات
            views = get_video_stats(video_id)
            with open("stats.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), animal, views])

            time.sleep(15)
        except Exception as e:
            print(f"⚠️ Error with {animal}: {e}")

    print("🎯 All 3 long videos uploaded successfully!")

if __name__ == "__main__":
    main()
