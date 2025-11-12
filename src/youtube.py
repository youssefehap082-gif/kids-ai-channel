import os
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
    service = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    print("✅ YouTube API connection established.")
    return service

def upload_video(file_path, title, description, tags, privacy="public", schedule_time_rfc3339=None):
    youtube = get_service()

    if not os.path.exists(file_path):
        print(f"❌ Video file not found: {file_path}")
        raise FileNotFoundError(file_path)
    else:
        print(f"🎥 Found video file: {file_path}")

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "15"
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    if schedule_time_rfc3339:
        request_body["status"]["publishAt"] = schedule_time_rfc3339
        request_body["status"]["privacyStatus"] = "private"

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    print(f"🚀 Uploading video: {title}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📦 Uploading progress: {int(status.progress() * 100)}%")

    if "id" in response:
        video_id = response["id"]
        print(f"✅ Successfully uploaded video: https://youtube.com/watch?v={video_id}")
        return video_id
    else:
        print("❌ Upload failed. Response:", response)
        raise Exception("Upload failed.")
