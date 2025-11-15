# scripts/youtube_uploader.py

import os
import time
import json
import logging
from pathlib import Path
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ===============================================================
#  AUTHENTICATION
# ===============================================================

def get_youtube_service():
    """
    Authenticates using OAuth credentials (client_id, secret, refresh_token).
    Returns YouTube API service client.
    """
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        raise RuntimeError("YouTube API keys missing.")

    creds_data = {
        "token": None,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": ["https://www.googleapis.com/auth/youtube.upload"],
    }

    creds = google.oauth2.credentials.Credentials(**creds_data)

    if creds.expired or not creds.valid:
        try:
            creds.refresh(Request())
        except Exception as e:
            logger.error("Failed to refresh token: %s", e)
            raise

    service = build("youtube", "v3", credentials=creds)
    return service


# ===============================================================
#  VIDEO UPLOAD
# ===============================================================

def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags=None,
    privacy_status="public",
    thumbnail_path=None,
    subtitles_path=None,
):
    """
    Uploads a video to YouTube with full metadata.
    Auto Retries 3 times if fails.
    """
    if tags is None:
        tags = []

    video_path = str(video_path)
    if not Path(video_path).exists():
        raise RuntimeError(f"Video does not exist: {video_path}")

    service = get_youtube_service()

    body = {
        "snippet": {
            "title": title[:95],  # YouTube limit 100 chars
            "description": description,
            "tags": tags,
            "categoryId": "15",  # Animals category is People & Blogs (default)
        },
        "status": {
            "privacyStatus": privacy_status
        },
    }

    media = MediaFileUpload(video_path, chunksize=4 * 1024 * 1024, resumable=True)

    for attempt in range(1, 4):  # 3 attempts
        try:
            logger.info(f"Uploading video (attempt {attempt}): {title}")

            request = service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Uploaded {int(status.progress() * 100)}%")

            video_id = response["id"]
            logger.info(f"Upload successful: https://youtu.be/{video_id}")

            # Add thumbnail
            if thumbnail_path and Path(thumbnail_path).exists():
                try:
                    service.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_path)
                    ).execute()
                    logger.info("Thumbnail added.")
                except Exception as e:
                    logger.warning("Thumbnail upload failed: %s", e)

            # Upload subtitles
            if subtitles_path and Path(subtitles_path).exists():
                try:
                    service.captions().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "language": "en",
                                "name": "English",
                                "videoId": video_id,
                                "isDraft": False,
                            }
                        },
                        media_body=MediaFileUpload(subtitles_path, mimetype="application/octet-stream"),
                    ).execute()
                    logger.info("Subtitles uploaded.")
                except Exception as e:
                    logger.warning("Subtitle upload failed: %s", e)

            return video_id

        except Exception as e:
            logger.error("Upload failed on attempt %s: %s", attempt, e)
            time.sleep(2 * attempt)

    raise RuntimeError("Video upload failed after 3 attempts.")


# ===============================================================
#  SHORT UPLOAD (Auto-detect Shorts)
# ===============================================================

def upload_short(video_path, title, description, tags=None, thumbnail_path=None):
    """
    Uploads a YouTube Short.
    Must be vertical & <60s — YouTube automatically treats it as #Shorts.
    """
    if tags is None:
        tags = []

    if "#shorts" not in title.lower():
        title += " #shorts"

    if "#shorts" not in description.lower():
        description += "\n#shorts"

    return upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status="public",
        thumbnail_path=thumbnail_path,
    )
