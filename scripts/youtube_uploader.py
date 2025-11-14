import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import google.auth
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv('YT_REFRESH_TOKEN') or os.getenv('YT_REFRESH_TOKEN'.upper()),
        token=None,
        client_id=os.getenv('YT_CLIENT_ID'),
        client_secret=os.getenv('YT_CLIENT_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
    creds.refresh(google.auth.transport.requests.Request())
    return build('youtube', 'v3', credentials=creds)
def upload_video(file_path, title, description, tags=None):
    youtube = get_youtube_service()
    body = {
        'snippet': {'title': title, 'description': description, 'tags': tags or []},
        'status': {'privacyStatus': 'public'}
    }
    media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True)
    req = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    res = None
    while res is None:
        status, res = req.next_chunk()
    if not res or 'id' not in res:
        raise RuntimeError('YouTube did not return video ID - upload failed')
    print('Uploaded video id:', res['id'])
    return res['id']
