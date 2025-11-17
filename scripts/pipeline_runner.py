"""
scripts/pipeline_runner.py
Full pipeline orchestrator (scaffold).
Usage: python scripts/pipeline_runner.py --topic "Lion" --n 10 --out ./out
"""
import os
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from scripts.generate_script import generate_for_topic
from scripts.tts import generate_tts_for_facts
from scripts.media_fetcher import fetch_media_for_topic
from scripts.thumbnail_generator import generate_thumbnail_variants, predict_best_thumbnail
from scripts.upload_youtube import upload_video
from scripts.error_recovery import recover_from_exception

logger = logging.getLogger("kids_ai.runner")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

def render_placeholder(facts, audios, media_map, out_path):
    # simple JSON "render" file for placeholder
    p = {
        "facts": facts,
        "audios": audios,
        "media": media_map,
        "ts": str(datetime.utcnow())
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)
    return out_path

def run_pipeline(topic: str, n:int=10, out_dir:str="./out"):
    try:
        os.makedirs(out_dir, exist_ok=True)
        res = generate_for_topic(topic, n)
        facts = res.get("facts", [])
        logger.info("Generated %d facts for %s using %s", len(facts), topic, res.get("provider_chain"))

        if not facts:
            raise RuntimeError("No facts generated")

        # media
        media_map = fetch_media_for_topic(topic, facts)

        # tts
        voices = ["eleven_male","eleven_female"]
        audios = generate_tts_for_facts(facts, voices)

        # thumbnail
        thumb_variants = generate_thumbnail_variants(base_image_path=(media_map.get(0,[None])[0] or ""), title_text=res.get("title",""))
        chosen_thumb = predict_best_thumbnail(thumb_variants)

        # render (placeholder)
        out_file = os.path.join(out_dir, f"{topic.replace(' ','_')}_{int(datetime.utcnow().timestamp())}.json")
        render_path = render_placeholder(facts, audios, media_map, out_file)

        # upload
        upload_res = upload_video(render_path, res.get("title"), res.get("description"), tags=[topic,"animals","facts"])

        run_log = {
            "topic": topic,
            "title": res.get("title"),
            "facts_count": len(facts),
            "providers": res.get("provider_chain"),
            "render": render_path,
            "thumbnail": chosen_thumb,
            "upload": upload_res,
            "ts": str(datetime.utcnow())
        }
        # write run log
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(out_dir, f"run_{int(datetime.utcnow().timestamp())}.json"), "w", encoding="utf-8") as fh:
            json.dump(run_log, fh, ensure_ascii=False, indent=2)

        logger.info("Pipeline success: %s", upload_res)
        return run_log

    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        try:
            recover_from_exception(e, context={"topic": topic})
        except Exception as rec:
            logger.error("Recovery failed: %s", rec)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--out", default="./out")
    args = parser.parse_args()
    result = run_pipeline(args.topic, args.n, args.out)
    print(json.dumps(result, indent=2, ensure_ascii=False))
