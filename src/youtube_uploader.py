# المسار: src/youtube_uploader.py

import os
import io
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src.config import (
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
)

SCOPES = ['https://www.googleapis.com/auth/upload.youtube']

def get_youtube_service():
    """
    يجهز خدمة اليوتيوب باستخدام الـ Refresh Token
    """
    creds = Credentials.from_authorized_user_info(
        info={
            "client_id": YT_CLIENT_ID,
            "client_secret": YT_CLIENT_SECRET,
            "refresh_token": YT_REFRESH_TOKEN,
            "token_uri": "https://oauth2.googleapis.com/token"
        },
        scopes=SCOPES
    )
    
    if creds.expired and creds.refresh_token:
        print("Refreshing YouTube token...")
        creds.refresh(Request())
    
    return build('youtube', 'v3', credentials=creds)

def schedule_video_upload(
    video_path: str, 
    metadata: dict, 
    schedule_time: datetime,
    is_short: bool = False
):
    """
    يرفع الفيديو ويجدوله (أو ينشره فورًا لو schedule_time=None)
    """
    print(f"Uploading video: {video_path}")
    youtube = get_youtube_service()
    
    title = metadata['title']
    if is_short and "#shorts" not in title:
        title += " #shorts"

    body = {
        'snippet': {
            'title': title,
            'description': metadata['description'],
            'tags': metadata['tags'],
            'categoryId': '15', # 15 = Pets & Animals
            'defaultLanguage': 'en', # مهم عشان الترجمة التلقائية
            'defaultAudioLanguage': 'en' # مهم عشان الترجمة التلقائية
        },
        'status': {
            'privacyStatus': 'private',
            'selfDeclaredMadeForKids': False
        }
    }
    
    if schedule_time:
        body['status']['publishAt'] = schedule_time.isoformat() + ".0Z"
        # الفيديو هيفضل private لحد ميعاد النشر وهيبقى public لوحده
    else:
        body['status']['privacyStatus'] = 'public' # (Test Run)
        
    try:
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
        
        video_id = response['id']
        print(f"✅ Video Upload Successful! ID: {video_id}")
        
        # --- قسم الترجمة اتحذف بالكامل ---
        # اليوتيوب هيعمل (English - Automatic) لوحده
        print("Skipping SRT upload. Relying on YouTube's automatic captions.")
        
        return video_id
        
    except Exception as e:
        print(f"Error during YouTube upload: {e}")
        return None
