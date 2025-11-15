#!/usr/bin/env python3
"""
main.py - Orchestrator
- picks animals
- generates scripts (via content_generator.py)
- fetches clips via utils.fetch_clips_for_animal
- creates video via video_creator.assemble_long_video / assemble_short
- uploads via youtube_uploader.upload_video and polls processing
"""

import os
import sys
import logging
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))  # ensure local imports work when run from repo root

from scripts.animal_selector import pick_n_unique
from scripts.content_generator import generate_facts_script
from scripts.utils import ensure_tmp, fetch_clips_for_animal, load_animal_database, write_json, load_animal_database as read_db
from scripts.video_creator import assemble_long_video, assemble_short
from scripts.voice_generator import generate_voice_with_failover
from scripts.youtube_uploader import upload_video, poll_processing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main_orchestrator")

TEST_RUN = os.getenv("TEST_RUN", "false").lower() == "true"
FIRST_RUN = os.getenv("FIRST_RUN", "true").lower() == "true"  # default true to run 1 long + 1 short first

TMP = ensure_tmp()
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PERF_FILE = DATA_DIR / "performance_data.json"
PERF_FILE.parent.mkdir(parents=True, exist_ok=True)
if not PERF_FILE.exists():
    write_json(PERF_FILE, {})


def safe_upload(file_path, title, desc, tags):
    try:
        vid = upload_video(str(file_path), title, desc, tags=tags)
        ok = poll_processing(vid, timeout_seconds=300)
        if not ok:
            logger.error("Video processed as FAILED: %s", vid)
            return None
        logger.info("Video successfully processed and ready: %s", vid)
        return vid
    except Exception as e:
        logger.exception("Upload or processing failed: %s", e)
        return None


def process_long_for_animal(animal_entry, voice_gender="male"):
    name = animal_entry["name"]
    logger.info("Processing long for: %s", name)
    long_script, _ = generate_facts_script(name, num_facts_long=10)
    script_text = "\n".join(long_script) + "\n\nDon't forget to subscribe and hit the bell for more!"
    voice_path = generate_voice_with_failover(script_text, preferred_gender=voice_gender)
    clips_urls = fetch_clips_for_animal(name, limit=6)
    if not clips_urls:
        raise RuntimeError(f"No clips found for {name}. Enable PEXELS/PIXABAY keys or add local assets.")
    # download clips
    from scripts.utils import download_file
    clip_paths = []
    for i, url in enumerate(clips_urls):
        dest = TMP / f"{name}_clip_{i}.mp4"
        try:
            download_file(url, dest)
            clip_paths.append(dest)
        except Exception:
            continue
    if not clip_paths:
        raise RuntimeError(f"No downloadable clips for {name} after attempts.")
    music = None
    assets_music = Path(__file__).resolve().parent.parent / "assets" / "music"
    if assets_music.exists():
        files = list(assets_music.glob("*.mp3"))
        music = files[0] if files else None

    out = assemble_long_video(clip_paths, voice_path, music_path=music, title_text=f"10 Facts About {name.title()}")
    title = f"10 Facts About {name.title()} — Amazing Animal Facts"
    desc = f"{title}\n\nFacts about the {name}.\nGenerated automatically. Subscribe for more.\n"
    tags = [name, "animals", "wildlife", "facts"]
    video_id = safe_upload(out, title, desc, tags)
    return video_id


def process_short_for_animal(animal_entry):
    name = animal_entry["name"]
    logger.info("Processing short for: %s", name)
    _, short_script = generate_facts_script(name, num_facts_long=10, num_facts_short=1)
    # short script is single fact
    script_text = short_script[0] + "\n\nDon't forget to subscribe and hit the bell for more!"
    voice_path = None  # shorts are music-only per requirements
    clips_urls = fetch_clips_for_animal(name, limit=3)
    if not clips_urls:
        raise RuntimeError(f"No clips for short {name}")
    from scripts.utils import download_file
    dest = TMP / f"{name}_short.mp4"
    download_file(clips_urls[0], dest)
    assets_music = Path(__file__).resolve().parent.parent / "assets" / "music"
    music = None
    if assets_music.exists():
        files = list(assets_music.glob("*.mp3"))
        music = files[0] if files else None
    out = assemble_short(dest, music_path=music)
    title = f"{name.title()} — Quick Fact"
    desc = f"Quick fact about {name}.\n#shorts #{name}"
    tags = [name, "shorts", "animals"]
    video_id = safe_upload(out, title, desc, tags)
    return video_id


def run_first_run():
    # first run: upload 1 long + 1 short (to validate everything)
    animals = pick_n_unique(2)
    long_vid = None
    try:
        long_vid = process_long_for_animal(animals[0], voice_gender="male")
    except Exception as e:
        logger.exception("First long failed: %s", e)
    try:
        short_vid = process_short_for_animal(animals[1])
    except Exception as e:
        logger.exception("First short failed: %s", e)
    return


def run_full_cycle():
    # full production: 2 longs + 5 shorts
    animals_long = pick_n_unique(2)
    for i, a in enumerate(animals_long):
        try:
            process_long_for_animal(a, voice_gender="male" if i % 2 == 0 else "female")
        except Exception as e:
            logger.exception("Long failed for %s: %s", a.get("name"), e)
    # 5 shorts
    shorts = pick_n_unique(5)
    for s in shorts:
        try:
            process_short_for_animal(s)
        except Exception as e:
            logger.exception("Short failed for %s: %s", s.get("name"), e)


if __name__ == "__main__":
    # Entry point
    logger.info("TEST_RUN=%s FIRST_RUN=%s", TEST_RUN, FIRST_RUN)
    if TEST_RUN:
        logger.info("Running TEST mode (1 long + 1 short)")
        run_first_run()
    else:
        # if FIRST_RUN true run the single-run validation, then exit
        if FIRST_RUN:
            logger.info("FIRST_RUN enabled. Running 1 long + 1 short validation.")
            run_first_run()
            logger.info("FIRST_RUN done. Edit workflow to disable FIRST_RUN for full daily runs.")
            sys.exit(0)
        logger.info("Running full production cycle (2 long + 5 shorts)")
        run_full_cycle()
    logger.info("Done.")
