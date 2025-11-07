# scripts/upload_youtube.py
import os, sys, json, requests
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

def upload(file_path, title, desc, tags, made_for_kids=True, privacy="public"):
    token = get_access_token()
    creds = Credentials(token)
    youtube = build('youtube', 'v3', credentials=creds, cache_discovery=False)
    body = {
        "snippet": {"title": title, "description": desc, "tags": tags, "categoryId": "1"},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": made_for_kids}
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/*')
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    res = None
    while res is None:
        status, res = req.next_chunk()
        if status:
            print("Uploading", int(status.progress()*100), "%")
    print("Uploaded. video id:", res["id"])
    return res["id"]

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv)>1 else "output/final_episode.mp4"
    script = {}
    try:
        script = json.load(open("output/script.json", encoding="utf-8"))
    except:
        script = {"title":"Whiteboard Episode"}
    title = script.get("title","Whiteboard Episode")
    desc_lines = [
        title,
        "",
        "Subscribe for new episodes!",
        "",
        "Hashtags: #kids #story #whiteboard #animated"
    ]
    desc = "\n".join(desc_lines)
    tags = ["kids stories","whiteboard","animated","storytime","bedtime"]
    upload(path, title, desc, tags, made_for_kids=True, privacy="public")
    # upload short
    short = "output/short_episode.mp4"
    if os.path.exists(short):
        upload(short, title + " (Short)", desc + "\nShort version", tags, made_for_kids=True, privacy="public")
