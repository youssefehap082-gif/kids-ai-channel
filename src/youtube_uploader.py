# المسار: src/youtube_uploader.py

import os
import json
import replicate
import time
from datetime import datetime, timedelta
import io

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

from src.config import (
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN,
    REPLICATE_API_TOKEN, WHISPER_MODEL
)

SCOPES = ['https://www.googleapis.com/auth/upload.youtube']
# ملف الـ client_secret.json هنبنيه من الـ Secrets
CLIENT_SECRET_JSON = {
    "web": {
        "client_id": YT_CLIENT_ID,
        "project_id": "your-project-id", # (مش مهم أوي للـ Refresh Token)
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": YT_CLIENT_SECRET,
        "redirect_uris": ["http://localhost:8080"]
    }
}

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
    
    # نتأكد إن الـ Token شغال
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
    
    # تعديل العنوان للـ Shorts (اليوتيوب بيحب كده)
    title = metadata['title']
    if is_short and "#shorts" not in title:
        title += " #shorts"

    body = {
        'snippet': {
            'title': title,
            'description': metadata['description'],
            'tags': metadata['tags'],
            'categoryId': '15' # 15 = Pets & Animals
        },
        'status': {
            'privacyStatus': 'private', # بنرفعه private الأول
            'selfDeclaredMadeForKids': False
        }
    }
    
    # لو في ميعاد جدولة
    if schedule_time:
        body['status']['privacyStatus'] = 'private' # لازم يكون private الأول
        body['status']['publishAt'] = schedule_time.isoformat() + ".0Z"
    else:
        # لو (Test Run)، انشره "public" علطول
        body['status']['privacyStatus'] = 'public'
        
    # --- عملية الرفع ---
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
        
        # لو كان مجدول، خليه public في الميعاد
        if schedule_time:
            print(f"Setting publish time to {schedule_time}...")
            video_update_body = {
                'id': video_id,
                'status': {
                    'privacyStatus': 'public' # بنغيره لـ public
                }
            }
            # (ملاحظة: الـ publishAt اتظبط في الـ insert)
            # الكود ده للتأكيد بس
            youtube.videos().update(
                part='status',
                body={'id': video_id, 'status': {'privacyStatus': 'public', 'publishAt': schedule_time.isoformat() + ".0Z"}}
            ).execute()
        
        return video_id
        
    except Exception as e:
        print(f"Error during YouTube upload: {e}")
        # (Req #2): التأكد. لو وصلنا هنا يبقى فشل
        return None

def generate_srt_from_audio(combined_vo_path: str) -> str:
    """
    يستخدم Whisper (via Replicate) لإنشاء ملف ترجمة SRT
    """
    print(f"Generating SRT for {combined_vo_path} using Whisper...")
    
    try:
        with open(combined_vo_path, "rb") as audio_file:
            output = replicate.run(
                WHISPER_MODEL,
                input={
                    "audio": audio_file,
                    "model": "large-v3",
                    "translate": False,
                    "language": "en",
                    "transcription": "srt" # أهم حاجة
                }
            )
        
        srt_content = output.get("transcription")
        if not srt_content:
            raise Exception("Whisper output was empty")
            
        print("SRT Generated successfully.")
        return srt_content
        
    except Exception as e:
        print(f"Error generating SRT: {e}")
        return None

def upload_subtitle(video_id: str, srt_content: str, language: str):
    """
    يرفع ملف الترجمة (SRT) بلغة معينة
    """
    print(f"Uploading subtitle {language} for video ID: {video_id}")
    youtube = get_youtube_service()
    
    try:
        # تحويل الـ srt string إلى bytes
        srt_bytes = srt_content.encode('utf-8')
        media_body = MediaIoBaseUpload(io.BytesIO(srt_bytes), mimetype='application/octet-stream')

        request = youtube.captions().insert(
            part='snippet',
            body={
                'snippet': {
                    'videoId': video_id,
                    'language': language,
                    'name': '', # اسم التراك (مش مهم)
                    'isDraft': False
                }
            },
            media_body=media_body
        )
        
        response = request.execute()
        print(f"Subtitle ({language}) uploaded. ID: {response['id']}")
        
    except Exception as e:
        # أحيانًا اليوتيوب بياخد وقت يعالج الفيديو، فبترفض الترجمة
        print(f"Warning: Could not upload subtitle {language}: {e}")
        if "processing" in str(e):
            print("Video is still processing. Skipping subtitles for now.")
