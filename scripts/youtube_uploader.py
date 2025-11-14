import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv('YT_REFRESH_TOKEN') or os.getenv('YTREFRESHTOKEN'),
        token=None,
        client_id=os.getenv('YT_CLIENT_ID') or os.getenv('YTCLIENTID'),
        client_secret=os.getenv('YT_CLIENT_SECRET') or os.getenv('YTCLIENTSECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def upload_video(file_path, title, description, tags=None, is_short=False):
    youtube = get_youtube_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or []
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
    media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True)
    req = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    res = None
    while res is None:
        status, res = req.next_chunk()
    return res
