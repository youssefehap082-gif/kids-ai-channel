# scripts/upload_youtube.py
import os, sys, json, requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")
CHANNEL_ID = os.environ.get("YT_CHANNEL_ID")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN and CHANNEL_ID):
    print("YouTube credentials missing in env.")
    sys.exit(1)

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
        "snippet": {"title": title, "description": desc, "tags": tags, "categoryId": "22"},
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
    OUT = "output"
    script = {}
    try:
        script = json.load(open(os.path.join(OUT,"script.json"), encoding="utf-8"))
    except:
        script = {"title":"Animal Facts", "description":"Auto generated", "tags":[]}
    title = script.get("title","Animal Facts")
    desc = script.get("description","Auto generated animal facts video")
    tags = script.get("tags", [])
    # upload main video
    main = os.path.join(OUT,"final_animal.mp4")
    if os.path.exists(main):
        vid = upload(main, title, desc, tags, made_for_kids=False, privacy="public")
    else:
        print("Main video not found:", main)
    # upload short
    short = os.path.join(OUT,"short_animal.mp4")
    if os.path.exists(short):
        upload(short, title + " (Short)", desc + "\nShort version", tags, made_for_kids=False, privacy="public")
