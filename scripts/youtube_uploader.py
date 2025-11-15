import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv('YT_REFRESH_TOKEN'),
        token=None,
        client_id=os.getenv('YT_CLIENT_ID'),
        client_secret=os.getenv('YT_CLIENT_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
    import google.auth.transport.requests
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def upload_video(file_path, title, description, tags=None, privacy='public'):
    youtube = get_youtube_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or []
        },
        'status': {
            'privacyStatus': privacy
        }
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    return response
