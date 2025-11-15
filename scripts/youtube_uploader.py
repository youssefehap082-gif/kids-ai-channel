import os, json, time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube"]

def get_youtube_service():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token"
    )
    # refresh token to get access token
    request = None
    try:
        # google auth will use default request internally
        creds.refresh(request=None)
    except Exception as e:
        # still attempt build; google client may handle refresh
        pass
    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def upload_video_with_caption(filepath, title, description, tags=None, is_short=False):
    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or []
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    media = MediaFileUpload(filepath, chunksize=-1, resumable=True)
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    try:
        status, response = req.next_chunk()
        while response is None:
            status, response = req.next_chunk()
    except Exception as e:
        print("Upload error:", e)
        raise
    return response
