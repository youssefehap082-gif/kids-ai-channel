import os
import time
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload


def get_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    creds.refresh(Request())
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload_video(file_path, title, description, tags=None, privacy="public"):
    youtube = get_service()
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["animals", "shorts", "funny", "wildlife"],
            "categoryId": "15"  # Pets & Animals
        },
        "status": {"privacyStatus": privacy}
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    print(f"🚀 Starting upload for: {title}")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    retry = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"📦 Uploading... {int(status.progress() * 100)}%")
        except Exception as e:
            print(f"⚠️ Upload error: {e}")
            retry += 1
            if retry > 3:
                print("❌ Too many errors, stopping upload.")
                return None
            time.sleep(5)

    if "id" in response:
        video_id = response["id"]
        print(f"✅ Upload complete! Video ID: {video_id}")
        return video_id
    else:
        print("❌ Upload failed, no video ID in response.")
        return None


def verify_upload(video_id):
    youtube = get_service()
    try:
        request = youtube.videos().list(
            part="snippet,status",
            id=video_id
        )
        response = request.execute()
        if response.get("items"):
            print(f"✅ Verified! Video is live: https://youtube.com/watch?v={video_id}")
            return True
        else:
            print("❌ Video not found after upload check.")
            return False
    except Exception as e:
        print(f"⚠️ Verification failed: {e}")
        return False
