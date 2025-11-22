import os
import sys
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

# التعديل هنا: خلينا الدالة تقبل tags و thumbnail_path
def upload_video(file_path, title, description, tags=[], thumbnail_path=None):
    print("🚀 Uploading to YouTube (STRICT MODE + THUMBNAIL)...")
    
    if not os.environ.get("YOUTUBE_REFRESH_TOKEN"):
        print("❌ Error: YOUTUBE_REFRESH_TOKEN is missing!")
        sys.exit(1)

    token_info = {
        "client_id": os.environ.get("YOUTUBE_CLIENT_ID"),
        "client_secret": os.environ.get("YOUTUBE_CLIENT_SECRET"),
        "refresh_token": os.environ.get("YOUTUBE_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token"
    }

    try:
        creds = Credentials.from_authorized_user_info(token_info)
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags, # بنضيف التاجز هنا
                "categoryId": "15"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        # 1. رفع الفيديو
        print("📤 Sending Video File...")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(file_path)
        )
        response = request.execute()
        video_id = response['id']
        print(f"✅ VIDEO UPLOADED! ID: {video_id}")

        # 2. رفع الثامبنيل (لو موجود)
        if thumbnail_path and os.path.exists(thumbnail_path):
            print(f"🖼️ Uploading Thumbnail for {video_id}...")
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=googleapiclient.http.MediaFileUpload(thumbnail_path)
                ).execute()
                print("✅ Thumbnail Set Successfully.")
            except Exception as e:
                print(f"⚠️ Thumbnail Upload Failed (Video is still safe): {e}")

        return video_id

    except Exception as e:
        print(f"❌ FATAL UPLOAD ERROR: {e}")
        sys.exit(1)
        
