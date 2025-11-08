import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    privacy="public",
    schedule_time_rfc3339=None,
):
    print("🚀 Starting YouTube upload...")

    creds = Credentials(
        None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "15",  # Pets & Animals
        },
        "status": {
            "privacyStatus": privacy,
        },
    }

    if schedule_time_rfc3339 and privacy == "private":
        body["status"]["publishAt"] = schedule_time_rfc3339
        body["status"]["privacyStatus"] = "private"

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"⬆️ Uploading... {int(status.progress() * 100)}%")

    print(f"✅ Upload complete! Video ID: {response['id']}")
    return response["id"]
