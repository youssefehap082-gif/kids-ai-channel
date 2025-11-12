# tools/uploader.py
import os, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")
YT_CHANNEL_ID = os.getenv("YT_CHANNEL_ID")

def get_youtube_service():
    if not all([YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN]):
        raise RuntimeError("YouTube credentials missing in env")
    creds_data = {
        "token": "", 
        "refresh_token": YT_REFRESH_TOKEN,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": YT_CLIENT_ID,
        "client_secret": YT_CLIENT_SECRET,
        "scopes": ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube.readonly"]
    }
    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET,
        scopes=creds_data["scopes"]
    )
    # refresh to get token
    creds.refresh(Request:=_import_("google.auth.transport.requests").auth_request.Request())
    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def upload_video_to_youtube(video_path, title, description, tags=None, privacyStatus="public"):
    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": privacyStatus
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = req.execute()
    return resp
