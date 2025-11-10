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
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def upload_video(file_path, title, description, tags, privacy="public", schedule_time_rfc3339=None):
    youtube = get_service()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "15"  # Animals category
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

    print(f"🚀 Starting YouTube upload: {title}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📦 Uploading... {int(status.progress() * 100)}%")

    if "id" in response:
        print(f"✅ Video uploaded successfully! ID: {response['id']}")
        return response["id"]
    else:
        print("❌ Upload failed:", response)
        return None


def list_recent_videos(limit=10):
    youtube = get_service()
    request = youtube.videos().list(
        part="id,snippet",
        myRating="like",
        maxResults=limit
    )
    response = request.execute()
    videos = [
        {"id": item["id"], "title": item["snippet"]["title"]}
        for item in response.get("items", [])
    ]
    return videos


def get_video_stats_bulk(video_ids):
    youtube = get_service()
    request = youtube.videos().list(
        part="statistics",
        id=",".join(video_ids)
    )
    response = request.execute()
    stats = [item.get("statistics", {}) for item in response.get("items", [])]
    return stats
