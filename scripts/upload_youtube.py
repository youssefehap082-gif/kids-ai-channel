# upload video using refresh token flow
import os, requests, sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")

def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    r.raise_for_status()
    return r.json()["access_token"]

def upload(path, title, desc, tags):
    token = get_access_token()
    creds = Credentials(token)
    youtube = build('youtube','v3',credentials=creds)
    body = {
      "snippet": {"title": title, "description": desc, "tags": tags, "categoryId": "22"},
      "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": True}
    }
    media = MediaFileUpload(path, chunksize=-1, resumable=True, mimetype='video/*')
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress()*100)}%")
    print("Done, video id:", resp["id"])

if __name__ == "__main__":
    upload("output/final_episode.mp4","Test Episode","Auto-generated episode","kids,story")
