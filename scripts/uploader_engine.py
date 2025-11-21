import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
import sys

def upload_video(file_path, title, description):
    print("🚀 Uploading to YouTube (STRICT MODE)...")
    
    # التأكد من وجود المفاتيح
    if not os.environ.get("YOUTUBE_REFRESH_TOKEN"):
        print("❌ Error: YOUTUBE_REFRESH_TOKEN is missing!")
        sys.exit(1) # وقف البرنامج فوراً

    token_info = {
        "client_id": os.environ.get("YOUTUBE_CLIENT_ID"),
        "client_secret": os.environ.get("YOUTUBE_CLIENT_SECRET"),
        "refresh_token": os.environ.get("YOUTUBE_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token"
    }

    try:
        creds = Credentials.from_authorized_user_info(token_info)
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["shorts", "animals", "nature"],
                    "categoryId": "15"
                },
                "status": {
                    "privacyStatus": "public", 
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=googleapiclient.http.MediaFileUpload(file_path)
        )
        response = request.execute()
        
        # لو وصلنا هنا يبقى نجحنا
        print(f"✅ REAL SUCCESS! Video is Live: https://youtu.be/{response['id']}")
        return response['id']

    except Exception as e:
        # هنا مربط الفرس: لو حصل خطأ، افضح الدنيا ووقف البرنامج
        print(f"❌ FATAL UPLOAD ERROR: {e}")
        sys.exit(1) # (Exit Code 1) يعني فشل ذريع، جيت هب هيحمر
