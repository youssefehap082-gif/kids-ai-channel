# scripts/youtube_uploader.py
"""
YouTube uploader utilities (production-ready).

Functions:
- get_youtube_service() -> googleapiclient.discovery.Resource
- upload_video(filepath, title, description, tags, thumbnail=None, subtitles=None, is_short=False, privacy='public') -> dict (video resource)
- upload_thumbnail(youtube, video_id, thumbnail_path) -> dict
- upload_captions(youtube, video_id, srt_path, language='en') -> dict

Requires these env vars to be set (via GitHub Secrets):
- YT_CLIENT_ID
- YT_CLIENT_SECRET
- YT_REFRESH_TOKEN
- YT_CHANNEL_ID

Note: This uses google-auth and googleapiclient.
"""
import os
import time
import logging
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, HttpRequest
import google.auth.transport.requests

logger = logging.getLogger("youtube_uploader")
logger.setLevel(logging.INFO)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.force-ssl"]


def get_youtube_service():
    """
    Build a youtube service using refresh token flow.
    Expects env vars:
      YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
    """
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        raise RuntimeError("YouTube OAuth credentials are missing in environment variables.")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )

    # Force refresh (so we have a valid access token)
    try:
        request = google.auth.transport.requests.Request()
        creds.refresh(request)
    except Exception as e:
        logger.warning("Credential refresh failed: %s", e)
        # still try building service; errors will surface at API call time

    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    return youtube


def _wait_upload(resumable_request: HttpRequest, max_seconds: int = 600):
    """
    Helper to run a resumable upload and wait until completion.
    Returns the response dict on success.
    """
    start = time.time()
    response = None
    while response is None:
        status, response = resumable_request.next_chunk()
        if status:
            logger.info("Upload progress: %s%%", int(status.progress() * 100))
        if time.time() - start > max_seconds:
            raise RuntimeError("Upload timed out after %s seconds" % max_seconds)
    return response


def upload_video(filepath: str,
                 title: str,
                 description: str,
                 tags: list | None = None,
                 thumbnail: str | None = None,
                 subtitles: str | None = None,
                 is_short: bool = False,
                 privacy: str = "public"):
    """
    Uploads a video using resumable upload and returns the uploaded video resource dict.
    Ensures we only return when a valid videoId is present.
    """
    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or []
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    if is_short:
        # Shorts are vertical and get #shorts tag; the uploader doesn't force vertical sizing,
        # but we add the tag to increase discovery.
        body["snippet"]["tags"] = (body["snippet"].get("tags", []) + ["shorts"])[:50]

    media = MediaFileUpload(filepath, chunksize=-1, resumable=True, mimetype="video/*")

    logger.info("Starting upload for %s", filepath)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    try:
        # perform resumable upload and wait
        response = _wait_upload(request)
        if not response or "id" not in response:
            raise RuntimeError("Upload completed but no video id in response: %s" % response)
        video_id = response["id"]
        logger.info("Upload finished. Video ID: %s", video_id)

        # upload thumbnail if provided
        if thumbnail:
            try:
                upload_thumbnail(youtube, video_id, thumbnail)
            except Exception as e:
                logger.warning("Thumbnail upload failed: %s", e)

        # upload subtitles if provided
        if subtitles:
            try:
                upload_captions(youtube, video_id, subtitles, language="en")
            except Exception as e:
                logger.warning("Captions upload failed: %s", e)

        # Wait for YouTube processing to finish a bit (optional)
        # We'll query the videos().list endpoint to ensure status exists
        for attempt in range(6):
            v = youtube.videos().list(part="processingDetails,status", id=video_id).execute()
            items = v.get("items", [])
            if items:
                logger.info("Video processing state: %s", items[0].get("processingDetails", {}).get("processingStatus"))
                break
            time.sleep(2)

        return response
    except Exception as e:
        logger.error("Video upload failed: %s", e)
        raise


def upload_thumbnail(youtube, video_id: str, thumbnail_path: str):
    """
    Uploads an image file as a video's thumbnail.
    """
    if not Path(thumbnail_path).exists():
        raise RuntimeError("Thumbnail file not found: %s" % thumbnail_path)
    media = MediaFileUpload(thumbnail_path)
    res = youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    logger.info("Thumbnail upload response: %s", res)
    return res


def upload_captions(youtube, video_id: str, srt_path: str, language: str = "en", name: str = "English"):
    """
    Upload captions (SRT) for the uploaded video.
    Uses the 'caption' insert endpoint. Note: the API requires
    privileges and the file must be small enough.
    """
    if not Path(srt_path).exists():
        raise RuntimeError("Captions file not found: %s" % srt_path)

    body = {
        "snippet": {
            "language": language,
            "name": name,
            "videoId": video_id,
            "isDraft": False,
        }
    }

    media = MediaFileUpload(srt_path, mimetype="application/octet-stream", resumable=True)

    logger.info("Uploading captions for video %s", video_id)
    req = youtube.captions().insert(part="snippet", body=body, media_body=media)

    # captions insert is resumable too; we run it similarly
    try:
        response = _wait_upload(req)
        logger.info("Captions uploaded: %s", response)
        return response
    except Exception as e:
        logger.error("Captions upload failed: %s", e)
        raise
