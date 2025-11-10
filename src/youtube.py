import os
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta

def get_service():
    """Create and return YouTube API service."""
    creds = Credentials(
        None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    creds.refresh(Request())
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    return youtube


def upload_video(file_path, title, description, tags=None, privacy="public", schedule_time_rfc3339=None):
    """Upload a video to YouTube with proper logging and error handling."""
    youtube = get_service()

    if tags is None:
        tags = ["Nature", "Wildlife", "Animals", "Facts"]

    # إعداد البيانات
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

    # لو في جدول نشر محدد
    if schedule_time_rfc3339:
        request_body["status"]["publishAt"] = schedule_time_rfc3339
        request_body["status"]["privacyStatus"] = "private"

    # رفع الفيديو
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    print(f"🚀 Starting upload: {title}")
    response = None

    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"📦 Uploading... {int(status.progress() * 100)}% done")
    except googleapiclient.errors.HttpError as e:
        print(f"❌ Upload failed with HTTP error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

    if response and "id" in response:
        print(f"✅ Upload complete! Video ID: {response['id']}")
        return response["id"]
    else:
        print(f"❌ Upload failed: {response}")
        return None


def list_recent_videos(limit=10):
    """List recent uploaded videos for verification."""
    youtube = get_service()
    request = youtube.search().list(
        part="id,snippet",
        forMine=True,
        type="video",
        order="date",
        maxResults=limit
    )
    response = request.execute()

    videos = [
        {"id": item["id"]["videoId"], "title": item["snippet"]["title"]}
        for item in response.get("items", [])
    ]
    print(f"📺 Found {len(videos)} recent videos.")
    return videos


def get_video_stats_bulk(video_ids):
    """Get statistics (views, likes, comments) for a list of video IDs."""
    youtube = get_service()
    request = youtube.videos().list(
        part="statistics",
        id=",".join(video_ids)
    )
    response = request.execute()
    stats = {
        item["id"]: item.get("statistics", {}) for item in response.get("items", [])
    }
    print(f"📊 Stats retrieved for {len(stats)} videos.")
    return stats


def auto_schedule_time(offset_hours=0):
    """Helper to schedule uploads at specific times (for global audience)."""
    time = datetime.utcnow() + timedelta(hours=offset_hours)
    return time.isoformat("T") + "Z"
