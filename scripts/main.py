# scripts/main.py
import os
import logging
from pathlib import Path
from datetime import datetime

from scripts.animal_selector import pick_animals
from scripts.content_generator import generate_facts_script
from scripts.voice_generator import generate_voice_with_fallback
from scripts.video_creator import assemble_long_video, assemble_short_video
from scripts.youtube_uploader import upload_youtube_video
from scripts.thumbnail_generator import generate_thumbnail
from scripts.seo_optimizer import build_title_desc_hashtags
from scripts.subtitles import generate_subtitles
from scripts.pexels_pixabay_fetcher import fetch_video_clips
from scripts.utils import safe_mkdir

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
OUTPUT = BASE / "output"
safe_mkdir(OUTPUT)


# TEST RUN (أول تشغيل)
TEST = os.getenv("TEST_RUN", "true").lower() == "true"


def process_long(animal):
    name = animal["name"]
    log.info(f"Processing LONG for: {name}")

    # نص الفيديو
    script, facts = generate_facts_script(name, num_facts_long=10)

    # تعليق صوتي
    voice_path = generate_voice_with_fallback(script, gender="male")

    # فيديوهات مجانية (Pexels + Pixabay)
    clips = fetch_video_clips(name, count=4)

    # تجميع الفيديو
    video_path = assemble_long_video(
        clips_paths=clips,
        voice_path=voice_path,
        title_text=name,
    )

    # صورة مصغرة
    thumb = generate_thumbnail(name)

    # ترجمة
    subs = generate_subtitles(script)

    # SEO
    title, desc, tags = build_title_desc_hashtags(name, facts, long=True)

    # رفع اليوتيوب
    upload_youtube_video(
        video_path,
        title,
        desc,
        thumb,
        tags,
        subs,
        privacy="public",
    )

    return video_path


def process_short(animal):
    name = animal["name"]
    log.info(f"Processing SHORT for: {name}")

    script, facts = generate_facts_script(name, num_facts_short=1)

    # لا تعليق صوتي في الشورتس
    voice = None

    # فيديوهات مجانية
    clips = fetch_video_clips(name, count=1)

    # تجميع شورت
    short_path = assemble_short_video(clips[0])

    # صورة مصغرة (لرفع اليوتيوب، اليوتيوب لا يعرضها ولكن نرفعها)
    thumb = generate_thumbnail(name)

    # SEO
    title, desc, tags = build_title_desc_hashtags(name, facts, long=False)

    upload_youtube_video(
        short_path,
        title,
        desc,
        thumb,
        tags,
        subtitles=None,
        privacy="public",
        short=True,
    )

    return short_path


def run_daily():
    log.info("Picking animals...")
    animals = pick_animals(7)   # 2 long + 5 shorts

    # 2 long
    for a in animals[:2]:
        try:
            process_long(a)
        except Exception as e:
            log.error(f"Long failed: {e}")

    # 4~5 shorts
    for a in animals[2:]:
        try:
            process_short(a)
        except Exception as e:
            log.error(f"Short failed: {e}")


def run_test():
    animals = pick_animals(2)   # 1 long + 1 short
    process_long(animals[0])
    process_short(animals[1])


if __name__ == "__main__":
    log.info(f"TEST_RUN = {TEST}")
    if TEST:
        run_test()
    else:
        run_daily()
