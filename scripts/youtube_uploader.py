"""
youtube_uploader.py
Uploads a video file to YouTube using OAuth2 refresh token credentials.
Requires these environment variables:
  - YT_CLIENT_ID
  - YT_CLIENT_SECRET
  - YT_REFRESH_TOKEN
  - YT_CHANNEL_ID

Uploads are resumable. After upload, the uploader polls processing status until 'succeeded'
or 'failed' (timeout configurable).
"""

import os
import time
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("youtube_uploader")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]


def get_youtube_service():
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        raise RuntimeError("YouTube credentials missing. Set YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )

    # Refresh token to obtain an access token
    try:
        request = None
        # google-auth library will refresh automatically when building service and making calls
        youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
        return youtube
    except Exception as e:
        logger.exception("Failed to build YouTube service: %s", e)
        raise


def upload_video(file_path: str, title: str, description: str, tags=None, categoryId="22", privacyStatus="public", language="en"):
    """
    Uploads a video file and returns the video ID on success.
    """
    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or [],
            "categoryId": categoryId,
            "defaultLanguage": language
        },
        "status": {
            "privacyStatus": privacyStatus,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    logger.info("Starting upload: %s", file_path)
    response = None
    try:
        status, response = request.next_chunk()
        while status is not None:
            logger.info("Upload progress: %s%%", int(status.progress() * 100))
            status, response = request.next_chunk()
    except Exception as e:
        logger.exception("Upload failed: %s", e)
        raise

    if not response or "id" not in response:
        raise RuntimeError(f"Upload did not return a video id: {response}")

    video_id = response["id"]
    logger.info("Upload completed. Video ID: %s", video_id)
    return video_id


def poll_processing(video_id: str, timeout_seconds: int = 300, interval: int = 8):
    """
    Polls the youtube API for processing status until succeeded or failed.
    Returns True if succeeded, False if failed or timed out.
    """
    youtube = get_youtube_service()
    logger.info("Polling processing status for video %s", video_id)
    elapsed = 0
    while elapsed < timeout_seconds:
        try:
            resp = youtube.videos().list(part="processingDetails,status", id=video_id).execute()
            items = resp.get("items", [])
            if not items:
                logger.warning("Video not found yet in API listing. Retrying...")
            else:
                pd = items[0].get("processingDetails", {})
                status = pd.get("processingStatus")
                logger.info("Processing status: %s", status)
                if status == "succeeded":
                    return True
                if status == "failed":
                    logger.error("Processing failed: %s", pd.get("processingFailureReason"))
                    return False
        except Exception as e:
            logger.debug("Polling exception (ignored): %s", e)

        time.sleep(interval)
        elapsed += interval

    logger.error("Polling timed out after %s seconds for video %s", timeout_seconds, video_id)
    return False


if __name__ == "__main__":
    # quick CLI for local testing (not used in Actions)
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    args = p.parse_args()
    vid = upload_video(args.file, args.title, args.description)
    ok = poll_processing(vid, timeout_seconds=300)
    print("Uploaded:", vid, "Processed:", ok)
