import os, time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import google.auth.transport.requests as grequests

YT_TOKEN_URI = 'https://oauth2.googleapis.com/token'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']

def get_youtube_service():
    client_id = os.getenv('YT_CLIENT_ID')
    client_secret = os.getenv('YT_CLIENT_SECRET')
    refresh_token = os.getenv('YT_REFRESH_TOKEN')
    if not (client_id and client_secret and refresh_token):
        raise RuntimeError('YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN must be set as environment variables.')

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=YT_TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    request = grequests.Request()
    try:
        creds.refresh(request)
    except Exception as e:
        raise RuntimeError(f'Failed to refresh YouTube credentials: {e}')
    youtube = build('youtube', 'v3', credentials=creds, cache_discovery=False)
    return youtube

def upload_video(file_path, title, description, tags=None, categoryId='22', privacyStatus='public'):
    youtube = get_youtube_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': categoryId
        },
        'status': {
            'privacyStatus': privacyStatus,
        },
        'notifySubscribers': False
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/*')
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = None
    print('Starting upload for', file_path)
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
        except Exception as e:
            print('Upload error, retrying chunk...:', e)
            time.sleep(2)
            continue
    print('Upload complete. Video id:', response.get('id'))
    return response

def upload_captions(video_id, srt_path, language='en', is_draft=False):
    youtube = get_youtube_service()
    media = MediaFileUpload(srt_path, mimetype='application/octet-stream', resumable=True)
    body = {
        'snippet': {
            'language': language,
            'name': f'captions_{language}',
            'videoId': video_id,
            'isDraft': is_draft
        }
    }
    try:
        req = youtube.captions().insert(part='snippet', body=body, media_body=media)
        resp = req.execute()
        return resp
    except Exception as e:
        raise RuntimeError(f'Caption upload failed: {e}')

def update_video_metadata(video_id, title=None, description=None, tags=None, privacyStatus=None):
    youtube = get_youtube_service()
    video = youtube.videos().list(part='snippet,status', id=video_id).execute()
    items = video.get('items', [])
    if not items:
        raise RuntimeError('Video not found: ' + video_id)
    snippet = items[0]['snippet']
    status = items[0].get('status', {})
    if title is not None:
        snippet['title'] = title
    if description is not None:
        snippet['description'] = description
    if tags is not None:
        snippet['tags'] = tags
    if privacyStatus is not None:
        status['privacyStatus'] = privacyStatus
    body = {
        'id': video_id,
        'snippet': snippet,
        'status': status
    }
    resp = youtube.videos().update(part='snippet,status', body=body).execute()
    return resp
