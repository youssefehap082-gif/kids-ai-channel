#!/usr/bin/env python3
import os, logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.auth.transport.requests

log = logging.getLogger('yt_uploader')

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']

def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv('YT_REFRESH_TOKEN'),
        token=None,
        client_id=os.getenv('YT_CLIENT_ID'),
        client_secret=os.getenv('YT_CLIENT_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
    try:
        creds.refresh(google.auth.transport.requests.Request())
    except Exception as e:
        log.exception("Credentials refresh failed: %s", e)
        raise
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def upload(file_path, title, description, tags=None, publishAt=None):
    """
    Uploads video and returns response dict. If publishAt provided (ISO8601), sets scheduled publish time.
    """
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
    if publishAt:
        body['status']['privacyStatus'] = 'private'
        body['status']['publishAt'] = publishAt

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    req = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    res = None
    try:
        status, res = req.next_chunk()
        return res
    except Exception as e:
        log.exception("Upload failed for file %s: %s", file_path, e)
        raise
