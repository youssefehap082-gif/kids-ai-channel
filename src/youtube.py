import os
from pathlib import Path
from typing import List, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")
YT_CHANNEL_ID = os.getenv("YT_CHANNEL_ID")

def yt_service():
    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET,
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube"
        ]
    )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)

def upload_video(path: Path, title: str, description: str, tags: List[str], 
                 privacy="private", schedule_time_rfc3339: Optional[str]=None):
    youtube = yt_service()
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:4800],
            "tags": tags[:500],
            "categoryId": "15"
        },
        "status": {
            "privacyStatus": "private" if schedule_time_rfc3339 else privacy,
            "selfDeclaredMadeForKids": False
        }
    }
    if schedule_time_rfc3339:
        body["status"]["publishAt"] = schedule_time_rfc3339
    media = MediaFileUpload(str(path), chunksize=-1, resumable=True, mimetype="video/*")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = req.next_chunk()
    return response
