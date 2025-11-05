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

def upload_video(file_path):
    token = get_access_token()
    creds = Credentials(token)
    youtube = build('youtube', 'v3', credentials=creds)
    title = "Max & Sam | Episode 1: The Little Star Map"
    description = """Max & Sam - Episode 1: The Little Star Map 🌟
A gentle short bedtime story for kids and families. Subscribe for new episodes!
#BedtimeStory #KidsStories #AnimatedStory"""
    tags = ["kids stories","bedtime story","animated story","family friendly","short stories","Max","Sam"]
    body = {
        "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "22"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": True}
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/*')
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    res = None
    while res is None:
        status, res = req.next_chunk()
        if status:
            print("Uploading", int(status.progress()*100), "%")
    print("Upload finished. video id:", res["id"])
    return res["id"]

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv)>1 else "output/final_episode.mp4"
    upload_video(path)
