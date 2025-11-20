import logging
import sys
import os

# === SETUP ENV ===
os.makedirs("logs", exist_ok=True)
os.makedirs("data/temp", exist_ok=True)
os.makedirs("data/output", exist_ok=True)

from scripts import (
    generate_script, fetch_media, tts, render_video, 
    upload_youtube, community_manager, error_recovery
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("logs/pipeline.log"), logging.StreamHandler(sys.stdout)]
)

def run_daily_cycle():
    logging.info(">>> STARTING DAILY PIPELINE (FULL RENDER MODE) <<<")
    
    try:
        topic = generate_script.select_topic()
        logging.info(f"Selected Topic: {topic}")

        script_data = generate_script.generate_full_script(topic)
        audio_paths = tts.generate_audio(script_data)
        media_assets = fetch_media.get_assets(topic, script_data)
        
        # Render
        video_path = render_video.render_long_video(script_data, audio_paths, media_assets)
        
        if not video_path:
            raise Exception("Video Rendering FAILED. No file produced.")
            
        # Upload
        logging.info(f"Uploading Long Video: {video_path}")
        upload_youtube.upload_video(video_path, script_data, is_short=False)
        
        logging.info(">>> SUCCESS <<<")

    except Exception as e:
        logging.critical(f"Pipeline Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_daily_cycle()