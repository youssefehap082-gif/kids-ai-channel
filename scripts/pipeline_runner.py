import logging
import sys
import os
from scripts import (
    generate_script, fetch_media, tts, render_video, 
    upload_youtube, community_manager, error_recovery
)

# === FIX: Ensure logs directory exists ===
os.makedirs("logs", exist_ok=True)
# =========================================

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_daily_cycle():
    logging.info(">>> STARTING DAILY PIPELINE <<<")
    
    try:
        # 1. Topic Selection
        topic = generate_script.select_topic()
        logging.info(f"Selected Topic: {topic}")

        # 2. Generate Content
        script_data = generate_script.generate_full_script(topic)
        
        # 3. Audio
        audio_paths = tts.generate_audio(script_data)
        
        # 4. Visuals
        media_assets = fetch_media.get_assets(topic, script_data)
        
        # 5. Render Long Video
        video_path = render_video.render_long_video(script_data, audio_paths, media_assets)
        
        # 6. Render Shorts
        shorts_paths = render_video.render_shorts(script_data, media_assets)
        
        # 7. Upload to YouTube
        if video_path:
            upload_youtube.upload_video(video_path, script_data, is_short=False)
            
        for short in shorts_paths:
            upload_youtube.upload_video(short, script_data, is_short=True)

        # 8. Community Post
        community_manager.post_daily_update(topic, video_path)

        logging.info(">>> PIPELINE COMPLETED SUCCESSFULLY <<<")

    except Exception as e:
        logging.critical(f"Pipeline Failed: {e}")
        error_recovery.handle_failure(e)
        sys.exit(1)

if __name__ == "__main__":
    run_daily_cycle()