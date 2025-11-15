import os
import random
import logging
from datetime import datetime
from pathlib import Path

# Local modules
from scripts.animal_selector import pick_animals
from scripts.content_generator import generate_facts_script
from scripts.voice_generator import generate_voice_with_failover
from scripts.video_creator import assemble_long_video, assemble_short_video
from scripts.youtube_uploader import upload_to_youtube
from scripts.utils import fetch_animal_clips, fetch_music_track, ensure_dir
from scripts.subtitles import generate_subtitles
from scripts.seo_optimizer import build_title, build_description, build_tags
from scripts.thumbnail_generator import generate_thumbnail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main_orchestrator")

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
OUT = BASE / "output"
ensure_dir(DATA)
ensure_dir(OUT)


# -------- GLOBAL CONFIG -------- #

TEST = os.getenv("TEST_RUN", "true").lower() == "true"

# 2 long videos + 4–6 shorts in production
LONG_VIDEOS_PER_DAY = 2
SHORTS_MIN = 4
SHORTS_MAX = 6


# -------- MAIN PIPELINE -------- #

def process_long_for_animal(animal):
    """
    Creates one long video:
    - Generates script
    - Generates voice
    - Gets clips + music
    - Assembles video
    - Generates subtitles
    - Generates thumbnail
    - Uploads to YouTube
    """
    name = animal["name"]
    logger.info(f"Processing LONG video for: {name}")

    # 1) Script (Mixed scientific + fun + viral)
    script, facts = generate_facts_script(name)

    # 2) Voice
    voice_path = generate_voice_with_failover(script, preferred_gender=random.choice(["male", "female"]))

    # 3) Fetch clips
    clips = fetch_animal_clips(name)
    if not clips:
        raise RuntimeError(f"No clips found for {name}")

    # 4) Fetch music
    music = fetch_music_track()

    # 5) Build title/description/SEO
    title = build_title(name, facts)
    description = build_description(name, facts)
    tags = build_tags(name, facts)

    # 6) Assemble full video
    final_video = assemble_long_video(
        clips_paths=clips,
        voice_path=voice_path,
        music_path=music,
        title_text=name.title(),
    )

    # 7) Subtitles
    subs_path = generate_subtitles(script, final_video)

    # 8) Thumbnail
    thumb_path = generate_thumbnail(name)

    # 9) Upload
    upload_id = upload_to_youtube(
        filepath=final_video,
        title=title,
        description=description,
        tags=tags,
        thumbnail=thumb_path,
        subtitles=subs_path,
        privacy="public"
    )

    return upload_id


def process_short_for_animal(animal):
    name = animal["name"]
    logger.info(f"Processing SHORT for: {name}")

    # Script → one fact
    _, facts = generate_facts_script(name, short_mode=True)
    short_fact = facts[0]

    # Fetch short clip
    clips = fetch_animal_clips(name, short_mode=True)
    if not clips:
        raise RuntimeError(f"No short clips found for {name}")

    # Music (no voice)
    music = fetch_music_track()

    # Assemble
    short_video = assemble_short_video(
        clip_path=clips[0],
        music_path=music,
    )

    title = f"{name.title()} Fact You Didn't Know!"
    description = f"Amazing {name} fact: {short_fact}"
    tags = [name, "animals", "wildlife", "shorts"]

    upload_id = upload_to_youtube(
        filepath=short_video,
        title=title,
        description=description,
        tags=tags,
        thumbnail=None,
        subtitles=None,
        is_short=True,
        privacy="public"
    )

    return upload_id


def run_first_run():
    """
    FIRST RUN = 1 long + 1 short
    This ensures:
    - API keys working
    - Upload works
    - MoviePy works
    - Voice works
    - Clips & music working
    """
    logger.info("FIRST_RUN enabled. Running 1 long + 1 short validation.")

    animals = pick_animals(2)

    # LONG
    try:
        process_long_for_animal(animals[0])
    except Exception as e:
        logger.error(f"First long failed: {e}")

    # SHORT
    try:
        process_short_for_animal(animals[1])
    except Exception as e:
        logger.error(f"First short failed: {e}")

    logger.info("FIRST_RUN completed.")


def run_production():
    """
    Daily production:
    2 longs + 4–6 shorts
    Distributed across best times for US audience
    """
    logger.info("PRODUCTION MODE: Running daily jobs")

    animals_long = pick_animals(LONG_VIDEOS_PER_DAY)
    animals_short = pick_animals(random.randint(SHORTS_MIN, SHORTS_MAX))

    # LONG videos
    for a in animals_long:
        try:
            process_long_for_animal(a)
        except Exception as e:
            logger.error(f"Long failed: {e}")

    # SHORT videos
    for a in animals_short:
        try:
            process_short_for_animal(a)
        except Exception as e:
            logger.error(f"Short failed: {e}")

    logger.info("Daily production completed.")


# ------------ ENTRY POINT ------------ #

if __name__ == "__main__":
    logger.info(f"TEST_RUN={TEST}")

    # If TEST_RUN=True → publish only 1 long + 1 short
    if TEST:
        run_first_run()
    else:
        run_production()
