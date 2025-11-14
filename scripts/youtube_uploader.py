# youtube_uploader.py - upload and set metadata using YouTube Data API
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']

def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv('YTREFRESHTOKEN'),
        token=None,
        client_id=os.getenv('YTCLIENTID'),
        client_secret=os.getenv('YTCLIENTSECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
    # refresh requires google.auth.transport.requests.Request - import lazily
    import google.auth.transport.requests
    creds.refresh(google.auth.transport.requests.Request())
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
