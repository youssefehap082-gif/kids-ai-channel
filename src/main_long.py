import os, random, time, textwrap
from datetime import datetime, timedelta
from src.media_sources import pick_video_urls
from src.tts import generate_tts
from src.compose import compose_video
from src.youtube import upload_video
from src.subtitles import add_subtitles
from src.utils import get_animal_facts
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip

def main():
    print("🎬 Generating Long Animal Fact Videos...")

    animals = ["Lion", "Tiger", "Elephant", "Panda", "Kangaroo", "Giraffe", "Koala", "Dolphin", "Cheetah", "Penguin"]
    random.shuffle(animals)

    for idx, animal in enumerate(animals[:3]):
        print(f"🐾 Generating video for: {animal}")

        # 1. جلب الحقائق
        facts = get_animal_facts(animal)
        script_text = " ".join(facts)

        # 2. توليد التعليق الصوتي (من ElevenLabs)
        tts_path = generate_tts(script_text, voice=random.choice(["Rachel", "Adam", "Domi"]))

        # 3. جلب الفيديوهات المناسبة للحيوان
        urls = pick_video_urls(animal, need=10, prefer_vertical=False)

        # 4. دمج الصوت مع الفيديوهات
        base_video = compose_video(urls, tts_path, min_duration=185)

        # 5. إضافة الترجمة النصية المتزامنة
        subtitled_video = add_subtitles(base_video, script_text)

        # 6. إضافة اللوجو في النهاية كـ outro
        logo_path = "assets/logo.png"
        outro = ImageClip(logo_path).set_duration(4).resize(height=200).set_position(("center", "center"))
        final_clip = CompositeVideoClip([VideoFileClip(subtitled_video), outro.set_start(VideoFileClip(subtitled_video).duration - 4)])
        final_path = f"/tmp/{animal.lower()}_final.mp4"
        final_clip.write_videofile(final_path, codec="libx264", audio_codec="aac")

        # 7. تجهيز البيانات للنشر
        title = f"10 Amazing Facts About the {animal} You Didn't Know!"
        desc = f"Discover 10 fascinating facts about the {animal}! 🐾\nSubscribe for more animal wonders!\n#Wildlife #Nature #Animals"
        tags = [animal, "animals", "wildlife", "facts"]

        # 8. رفع الفيديو
        upload_video(final_path, title, desc, tags, privacy="public")

        print(f"✅ Done uploading video about {animal}")
        time.sleep(10)  # delay بسيط بين كل فيديو

if __name__ == "__main__":
    main()
