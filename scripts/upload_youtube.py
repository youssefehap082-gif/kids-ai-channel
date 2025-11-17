"""
scripts/upload_youtube.py
Placeholder uploader: integrates with YouTube Data API (OAuth2) when implemented.
Expects env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, YT_CHANNEL_ID
"""
import os, logging
logger = logging.getLogger("kids_ai.upload")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

def upload_video(file_path: str, title: str, description: str, tags: list, privacyStatus="public"):
    # Placeholder: replace with real googleapiclient flow
    logger.info("Upload stub: %s -> title=%s", file_path, title)
    return {"status":"ok","videoId":"STUB123","url":"https://youtu.be/STUB123"}
