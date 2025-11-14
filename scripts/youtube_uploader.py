import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
def get_service():
    rt = os.getenv('YT_REFRESH_TOKEN'); cid=os.getenv('YT_CLIENT_ID'); cs = os.getenv('YT_CLIENT_SECRET')
    if not (rt and cid and cs): raise RuntimeError('YouTube secrets missing')
    creds = Credentials(None, refresh_token=rt, token=None, client_id=cid, client_secret=cs, token_uri='https://oauth2.googleapis.com/token')
    from google.auth.transport.requests import Request
    creds.refresh(Request())
    return build('youtube','v3', credentials=creds)
def upload_video(path, title, desc, tags=None):
    yt = get_service()
    body = {'snippet':{'title':title,'description':desc,'tags':tags or []}, 'status':{'privacyStatus':'public'}}
    media = MediaFileUpload(str(path), chunksize=-1, resumable=True)
    req = yt.videos().insert(part='snippet,status', body=body, media_body=media)
    res=None
    while res is None:
        status, res = req.next_chunk()
    return res
