#!/usr/bin/env python3
"""
Main orchestrator for the YouTube animal channel automation.

Responsibilities:
- Load configuration and environment variables
- Pick animals for today's batch (uses animal_selector)
- For each animal:
    - Generate script (content_generator) with fallback across AI providers
    - Generate voice (voice_generator) with tts failover
    - Fetch / prepare footage (pexels/pixabay fetcher)
    - Assemble long + shorts (video_creator)
    - Generate subtitle files and SEO metadata (tools/subtitles + seo)
    - Upload videos to YouTube (youtube_uploader)
- Implements safe retries, logging and first-run TEST mode:
    - TEST_RUN=True => publish only 1 long + 1 short (immediate)
    - TEST_RUN=False => production run (2 long + 4-6 shorts distributed)
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import time
import random

# Ensure scripts/ is on python path when run inside GH Actions
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# local modules (will be provided separately)
from scripts.animal_selector import pick_n_unique, mark_used
from scripts.content_generator import generate_facts_script
from scripts.voice_generator import generate_voice_with_failover
from scripts.video_creator import assemble_long_video, assemble_short
from scripts.youtube_uploader import upload_video_with_metadata
from scripts.utils import ensure_data_folders, load_json, save_json

# tools
from tools.subtitles import write_srt_from_transcript

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("main_orchestrator")

# Environment toggles
TEST = os.getenv("TEST_RUN", "true").lower() == "true"
FIRST_RUN = os.getenv("FIRST_RUN", "true").lower() == "true"

# Output folders
DATA_DIR = ROOT / "data"
TMP_DIR = ROOT / "assets" / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Basic workflow settings
LONGS_PER_DAY = 2
SHORTS_PER_DAY_MIN = 4
SHORTS_PER_DAY_MAX = 6

# Retry helper
def retry(fn, tries=3, delay=1, allowed_exceptions=(Exception,), onfail=None, *a, **kw):
    last_exc = None
    for attempt in range(1, tries + 1):
        try:
            return fn(*a, **kw)
        except allowed_exceptions as e:
            last_exc = e
            logger.warning("Attempt %d/%d failed for %s: %s", attempt, tries, getattr(fn, "__name__", fn), e)
            if attempt < tries:
                time.sleep(delay * attempt)
    logger.error("All %d attempts failed for %s", tries, getattr(fn, "__name__", fn))
    if onfail:
        return onfail(last_exc)
    raise last_exc

def process_long_for_animal(animal_entry, voice_gender="male"):
    name = animal_entry["name"]
    logger.info("Processing long for: %s", name)
    # 1) Generate facts script (with provider-fallback internal)
    try:
        meta, script_text = generate_facts_script(name, num_facts_long=10, style="mixed")
    except Exception as e:
        logger.exception("Failed to generate facts script for %s: %s", name, e)
        raise

    # 2) Generate TTS audio (failover inside function)
    try:
        voice_path = retry(
            generate_voice_with_failover,
            tries=3,
            delay=2,
            allowed_exceptions=(Exception,),
            onfail=lambda e: (_ for _ in ()).throw(RuntimeError(f"All TTS failed for {name}: {e}")),
            script_text=script_text,
            preferred_gender=voice_gender,
            voice_label=f"{name}_long"
        )
    except Exception as e:
        logger.exception("Voice generation failed for %s: %s", name, e)
        raise

    # 3) Fetch visuals (pexels/pixabay) - function assumed to return list of file paths
    try:
        from scripts.pexels_pixabay_fetcher import fetch_media_for_animal
        clips = retry(fetch_media_for_animal, tries=2, delay=2, allowed_exceptions=(Exception,), onfail=lambda e: [])
    except Exception as e:
        logger.warning("Media fetcher missing or failed: %s", e)
        clips = []

    if not clips:
        logger.warning("No clips found via fetcher; falling back to local assets if any.")
        # fallback: use assets/music/background or placeholder (caller should handle)
        # For now we will still proceed; assemble_long_video will raise if no valid clips.

    # 4) Choose music if available
    music_path = None
    candidate_music = list((ROOT / "assets" / "music").glob("*"))
    if candidate_music:
        music_path = str(random.choice(candidate_music))

    # 5) Assemble video
    try:
        out_path = TMP_DIR / f"{name.replace(' ', '_')}_long_{int(time.time())}.mp4"
        retry(
            assemble_long_video,
            tries=2,
            delay=2,
            allowed_exceptions=(Exception,),
            out_path=out_path,
            clips_paths=clips,
            voice_path=voice_path,
            music_path=music_path,
            title_text=meta.get("title") or f"10 facts about {name}"
        )
    except Exception as e:
        logger.exception("Failed to assemble long video for %s: %s", name, e)
        raise

    # 6) Generate subtitles
    srt_path = TMP_DIR / f"{name.replace(' ', '_')}_long.srt"
    try:
        write_srt_from_transcript(script_text, srt_path)
    except Exception as e:
        logger.warning("Subtitle creation failed for %s: %s", name, e)

    # 7) SEO metadata
    title = meta.get("title") or f"10 Facts About {name} — Amazing Animal Facts"
    description = meta.get("description") or script_text[:4000]
    tags = meta.get("tags") or [name, "animals", "facts", "wildlife"]

    return {
        "video_path": str(out_path),
        "srt": str(srt_path),
        "title": title,
        "description": description,
        "tags": tags,
        "is_long": True,
        "animal": name,
    }

def process_short_for_animal(animal_entry, index=0):
    name = animal_entry["name"]
    logger.info("Processing short for: %s", name)
    # Short script (single fact)
    try:
        _, short_script = generate_facts_script(name, num_facts_long=1, num_facts_short=1, style="viral")
    except Exception as e:
        logger.exception("Failed to generate short script for %s: %s", name, e)
        raise

    # Generate voice
    try:
        voice_path = generate_voice_with_failover(short_script, preferred_gender="female", voice_label=f"{name}_short_{index}")
    except Exception as e:
        logger.exception("Short TTS failed for %s: %s", name, e)
        raise

    # fetch one clip
    try:
        from scripts.pexels_pixabay_fetcher import fetch_media_for_animal
        clips = fetch_media_for_animal(name, max_results=2)
    except Exception as e:
        logger.warning("Short media fetch failed: %s", e)
        clips = []

    if not clips:
        logger.warning("No media for short; attempting to use a random long clip fallback.")
        clips = []  # let video_creator raise if needed

    # choose music
    music_path = None
    candidate_music = list((ROOT / "assets" / "music").glob("*"))
    if candidate_music:
        music_path = str(random.choice(candidate_music))

    # assemble
    try:
        out_path = TMP_DIR / f"{name.replace(' ', '_')}_short_{int(time.time())}.mp4"
        retry(
            assemble_short,
            tries=2,
            delay=1,
            allowed_exceptions=(Exception,),
            clip_path=(clips[0] if clips else None),
            music_path=music_path,
            out_path=out_path
        )
    except Exception as e:
        logger.exception("Failed to assemble short for %s: %s", name, e)
        raise

    # subtitles
    srt_path = TMP_DIR / f"{name.replace(' ', '_')}_short.srt"
    try:
        write_srt_from_transcript(short_script, srt_path)
    except Exception as e:
        logger.warning("Short subtitle creation failed for %s: %s", name, e)

    # SEO metadata
    title = f"{name} — Quick Fact"
    description = short_script
    tags = [name, "shorts", "animal-facts"]

    return {
        "video_path": str(out_path),
        "srt": str(srt_path),
        "title": title,
        "description": description,
        "tags": tags,
        "is_long": False,
        "animal": name,
    }

def upload_with_retry(item):
    try:
        # Upload and return upload response
        resp = retry(
            upload_video_with_metadata,
            tries=3,
            delay=2,
            allowed_exceptions=(Exception,),
            onfail=lambda e: (_ for _ in ()).throw(RuntimeError(f"Uploader failed: {e}")),
            **item
        )
        return resp
    except Exception as e:
        logger.exception("Upload failed: %s", e)
        return None

def run_first_run():
    """If FIRST_RUN enabled, do a single test: 1 long + 1 short and then exit."""
    logger.info("FIRST_RUN enabled. Running 1 long + 1 short validation.")
    # pick 2 animals (or 1 if TEST forces)
    animals = pick_n_unique(2) if not TEST else pick_n_unique(2)
    successes = []
    try:
        long_item = process_long_for_animal(animals[0])
        resp_long = upload_with_retry(long_item)
        successes.append(("long", resp_long))
    except Exception as e:
        logger.error("First long failed: %s", e)

    try:
        short_item = process_short_for_animal(animals[1])
        resp_short = upload_with_retry(short_item)
        successes.append(("short", resp_short))
    except Exception as e:
        logger.error("First short failed: %s", e)

    logger.info("FIRST_RUN done. Edit workflow to disable FIRST_RUN for full daily runs.")
    return successes

def distribute_and_schedule_uploads(long_items, short_items):
    """
    In production this function would schedule uploads across the day.
    In GH Actions we perform uploads immediately but can compute scheduled publish times for metadata.
    """
    # Basic simple distribution:
    now = datetime.utcnow()
    scheduled_times = []
    # spread longs: morning + evening
    for i, itm in enumerate(long_items):
        publish_at = now.replace(hour=7 + i*6, minute=0, second=0, microsecond=0)
        scheduled_times.append(publish_at.isoformat() + "Z")
        itm["publish_at"] = publish_at.isoformat() + "Z"
    # spread shorts: between 9am..20pm
    for i, itm in enumerate(short_items):
        hour = 9 + (i * max(1, (12 // max(1, len(short_items)))))
        publish_at = now.replace(hour=min(23, hour), minute=0, second=0, microsecond=0)
        itm["publish_at"] = publish_at.isoformat() + "Z"
    return long_items + short_items

def main():
    logger.info("Initialized data folder")
    ensure_data_folders(ROOT)

    # Read animals
    num_longs = 1 if TEST else LONGS_PER_DAY
    num_shorts = 1 if TEST else random.randint(SHORTS_PER_DAY_MIN, SHORTS_PER_DAY_MAX)

    # pick animals
    animals = pick_n_unique(num_longs + num_shorts)
    logger.info("Selected animals: %s", [a["name"] for a in animals])

    long_items = []
    short_items = []

    # FIRST_RUN quick test override
    if FIRST_RUN:
        run_first_run()
        return

    # process longs
    for i in range(num_longs):
        try:
            a = animals[i]
            item = process_long_for_animal(a, voice_gender=("male" if i % 2 == 0 else "female"))
            long_items.append(item)
            mark_used(a["name"])
        except Exception as e:
            logger.exception("Long processing failed for index %d: %s", i, e)
            continue

    # process shorts
    for j in range(num_shorts):
        try:
            a = animals[num_longs + j]
            item = process_short_for_animal(a, index=j)
            short_items.append(item)
            mark_used(a["name"])
        except Exception as e:
            logger.exception("Short processing failed for index %d: %s", j, e)
            continue

    # schedule/distribute
    batch = distribute_and_schedule_uploads(long_items, short_items)

    # upload each (immediate uploading; uploader should honor publish_at if supported)
    for itm in batch:
        logger.info("Uploading item for %s (long=%s)", itm.get("animal"), itm.get("is_long"))
        resp = upload_with_retry(itm)
        if resp:
            logger.info("Upload succeeded for %s", itm.get("animal"))
        else:
            logger.error("Upload failed for %s", itm.get("animal"))

    logger.info("Run completed")

if __name__ == "__main__":
    main()
