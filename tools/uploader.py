# tools/uploader.py
import os, json, time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import google.auth.transport.requests as gr

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")
YT_CHANNEL_ID = os.getenv("YT_CHANNEL_ID")

def get_youtube_service():
    if not all([YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN]):
        raise RuntimeError("YouTube credentials missing in env (YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN)")
    creds = Credentials(
        token=None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube"]
    )
    request = gr.Request()
    creds.refresh(request)
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    return youtube

def upload_video_to_youtube(video_path, title, description, tags=None, privacyStatus="public", thumbnail_path=None):
    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": privacyStatus
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    try:
        resp = req.execute()
        video_id = resp.get("id")
        if thumbnail_path and Path(thumbnail_path).exists():
            try:
                youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumbnail_path)).execute()
            except Exception as e:
                print("[uploader] thumbnail upload failed:", e)
    except Exception as e:
        resp = {"error": str(e)}
    return resp
