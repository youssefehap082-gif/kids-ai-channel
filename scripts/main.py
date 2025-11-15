import os
import random
import logging
from datetime import datetime
from scripts.animal_selector import choose_animals_for_day
from scripts.content_generator import generate_facts_script
from scripts.voice_generator import tts_with_failover
from scripts.pexels_pixabay_fetcher import fetch_videos_for_animal
from scripts.video_creator import assemble_long_video, assemble_short
from scripts.youtube_uploader import upload_youtube_video
from scripts.utils import load_json, save_json, safe_mkdir
from scripts.subtitles import generate_subtitles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = "data"
USED_ANIMALS = f"{DATA_DIR}/used_animals.json"
PERFORMANCE_DATA = f"{DATA_DIR}/performance_data.json"
ANIMAL_DB = f"{DATA_DIR}/animal_database.json"

safe_mkdir(DATA_DIR)

TEST_RUN = os.getenv("TEST_RUN", "true").lower() == "true"

# CONSTANTS
LONG_PER_DAY = 2
SHORT_PER_DAY_MIN = 4
SHORT_PER_DAY_MAX = 6


def run_first_test_run():
    logger.info("TEST RUN: 1 long + 1 short")
    animals = choose_animals_for_day(2)

    # Process LONG
    try:
        name = animals[0]
        logger.info(f"Processing test long video for: {name}")

        long_script, _ = generate_facts_script(name, num_facts_long=8)
        voice_path = tts_with_failover(long_script, gender="male")
        clips = fetch_videos_for_animal(name)
        subtitles = generate_subtitles(long_script)
        final = assemble_long_video(
            clips_paths=clips[:6],
            voice_path=voice_path,
            music_path=None,
            title_text=f"{name.title()} Facts",
            out_path=f"output_test_long_{name}.mp4",
        )
        upload_youtube_video(
            path=str(final),
            title=f"{name.title()} – Amazing Facts (TEST RUN)",
            desc="Test video for pipeline.",
            tags=[name, "animals", "facts"],
            privacy="private",
            subtitles=subtitles,
        )
    except Exception as e:
        logger.error(f"ERROR long test: {e}")

    # Process SHORT
    try:
        name = animals[1]
        logger.info(f"Processing test short video for: {name}")
        _, short_script = generate_facts_script(name, num_facts_short=1)
        clips = fetch_videos_for_animal(name)
        final = assemble_short(
            clip_path=clips[0],
            music_path=None,
            out_path=f"output_test_short_{name}.mp4",
        )
        upload_youtube_video(
            path=str(final),
            title=f"{name.title()} — 1 Quick Fact (TEST)",
            desc="Short test video.",
            tags=[name, "shorts"],
            privacy="private",
        )
    except Exception as e:
        logger.error(f"ERROR short test: {e}")

    logger.info("TEST RUN COMPLETE")


def run_production():
    logger.info("Production Mode STARTED")

    num_shorts = random.randint(SHORT_PER_DAY_MIN, SHORT_PER_DAY_MAX)
    animals = choose_animals_for_day(LONG_PER_DAY + num_shorts)

    long_animals = animals[:LONG_PER_DAY]
    short_animals = animals[LONG_PER_DAY:]

    logger.info(f"Today's animals LONG: {long_animals}")
    logger.info(f"Today's animals SHORT: {short_animals}")

    # LONG VIDEOS
    for animal in long_animals:
        try:
            logger.info(f"Processing LONG for: {animal}")

            long_script, _ = generate_facts_script(animal, num_facts_long=10)
            voice_path = tts_with_failover(long_script, gender="male")
            clips = fetch_videos_for_animal(animal)
            subtitles = generate_subtitles(long_script)

            final = assemble_long_video(
                clips_paths=clips[:10],
                voice_path=voice_path,
                music_path=None,
                title_text=f"{animal.title()} Facts",
                out_path=f"final_long_{animal}.mp4",
            )

            upload_youtube_video(
                path=str(final),
                title=f"{animal.title()} – Mind-Blowing Facts",
                desc=f"Amazing facts about {animal}.",
                tags=[animal, "animals", "facts"],
                privacy="public",
                subtitles=subtitles,
            )

        except Exception as e:
            logger.error(f"LONG FAILED for {animal}: {e}")

    # SHORT VIDEOS
    for animal in short_animals:
        try:
            logger.info(f"Processing SHORT for: {animal}")

            _, short_script = generate_facts_script(animal, num_facts_short=1)
            clips = fetch_videos_for_animal(animal)

            final = assemble_short(
                clip_path=clips[0],
                music_path=None,
                out_path=f"final_short_{animal}.mp4",
            )

            upload_youtube_video(
                path=str(final),
                title=f"{animal.title()} Fact in 10 Seconds",
                desc=f"Quick fact about {animal}.",
                tags=[animal, "shorts", "facts"],
                privacy="public",
            )

        except Exception as e:
            logger.error(f"SHORT FAILED for {animal}: {e}")

    logger.info("PRODUCTION COMPLETE")


def main():
    # First: Ensure animal DB exists
    if not os.path.exists(ANIMAL_DB):
        from scripts.fetch_wikipedia import generate_animal_database
        logger.info("Animal DB missing — Generating…")
        generate_animal_database()

    if TEST_RUN:
        run_first_test_run()
    else:
        run_production()


if __name__ == "__main__":
    main()
