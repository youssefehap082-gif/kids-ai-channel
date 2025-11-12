# src/youtube.py
import os
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.environ.get("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("YT_CLIENT_ID"),
        client_secret=os.environ.get("YT_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube"]
    )
    creds.refresh(Request=None) if False else None  # placeholder to avoid linter noise
    # build with provided credentials using OAuth flow refresh — the google client will refresh automatically
    service = build("youtube", "v3", credentials=creds, cache_discovery=False)
    return service

def upload_video(file_path, title, description, tags=None, language="en", privacy="public", retry=3):
    """
    Upload video, return video_id on success, else raise exception.
    """
    # create credentials using oauth refresh flow (google oauth library will refresh automatically)
    creds = Credentials(
        None,
        refresh_token=os.environ.get("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("YT_CLIENT_ID"),
        client_secret=os.environ.get("YT_CLIENT_SECRET"),
    )

    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22",
            "defaultLanguage": language
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    attempt = 0
    while attempt < retry:
        try:
            print(f"🚀 Starting upload attempt {attempt+1} for {os.path.basename(file_path)}")
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"📦 Uploading... {int(status.progress() * 100)}%")
            if "id" in response:
                video_id = response["id"]
                print(f"✅ Upload finished: https://youtu.be/{video_id}")
                return video_id
            else:
                raise Exception("Upload completed but no video id returned.")
        except Exception as e:
            attempt += 1
            print(f"⚠️ Upload error (attempt {attempt}): {e}")
            if attempt < retry:
                backoff = 10 * attempt
                print(f"⏳ Waiting {backoff}s then retrying...")
                time.sleep(backoff)
            else:
                raise

def upload_captions(video_id, srt_path, language="en", name="English (auto)"):
    """
    Upload SRT as captions to a video. Returns caption id.
    """
    creds = Credentials(
        None,
        refresh_token=os.environ.get("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("YT_CLIENT_ID"),
        client_secret=os.environ.get("YT_CLIENT_SECRET"),
    )
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"SRT file not found: {srt_path}")

    # Snippet for captions insert
    body = {
        "snippet": {
            "videoId": video_id,
            "language": language,
            "name": name,
            "isDraft": False
        }
    }

    media = MediaFileUpload(srt_path, mimetype="application/octet-stream", resumable=True)
    request = youtube.captions().insert(part="snippet", body=body, media_body=media)
    response = request.execute()
    print(f"✅ Captions uploaded: id={response.get('id')}")
    return response.get("id")
