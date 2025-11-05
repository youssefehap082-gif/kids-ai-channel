# scripts/upload_youtube.py
import os, requests, sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")
CHANNEL_ID = os.environ.get("YT_CHANNEL_ID")

def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    r.raise_for_status()
    return r.json()["access_token"]

def upload_video(file_path, title, description, tags):
    token = get_access_token()
    creds = Credentials(token)
    youtube = build('youtube', 'v3', credentials=creds)
    body = {
      "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "22"},
      "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": True}
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/*')
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    res = None
    while res is None:
        status, res = req.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress()*100)}%")
    print("Done, video id:", res["id"])
    return res["id"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/upload_youtube.py final_episode.mp4")
        sys.exit(1)
    path = sys.argv[1]
    upload_video(path, "Hazem & Sheh Madwar - Auto Episode", "Auto-generated episode. Subscribe for new episodes!", ["kids","story","animated"])
