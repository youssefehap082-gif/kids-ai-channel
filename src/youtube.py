import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
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
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, tags, privacy="public"):
    youtube = get_service()
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "15"
        },
        "status": {"privacyStatus": privacy}
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    print(f"🚀 Uploading video: {title}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📦 {int(status.progress() * 100)}% uploaded")
    if "id" in response:
        print(f"✅ Uploaded: https://youtube.com/watch?v={response['id']}")
        return response["id"]
    else:
        raise Exception("Upload failed")
