from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os, time

def upload_video(video_path, title, desc, tags, thumb_path=None, privacy="public", schedule_time_rfc3339=None):
    from google.oauth2.credentials import Credentials
    creds = Credentials(
        None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET")
    )

    youtube = build("youtube", "v3", credentials=creds)
    request_body = {
        "snippet": {"title": title, "description": desc, "tags": tags, "categoryId": "15"},
        "status": {"privacyStatus": privacy},
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response.get("id")
    print(f"✅ Uploaded successfully: https://youtu.be/{video_id}")

    if thumb_path:
        youtube.thumbnails().set(videoId=video_id, media_body=thumb_path).execute()

    # ✳️ تعليق تلقائي بعد الرفع
    try:
        comment_text = "Which animal do you want next? 🐾 Comment below!"
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {"snippet": {"textOriginal": comment_text}}
                }
            }
        ).execute()
        print("💬 Posted auto comment successfully!")
    except Exception as e:
        print(f"⚠️ Failed to post comment: {e}")

    return video_id
