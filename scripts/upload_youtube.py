# scripts/upload_youtube.py
import os, sys, json, requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from pathlib import Path

CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")
CHANNEL_ID = os.environ.get("YT_CHANNEL_ID")

OUT = Path(sys.argv[1] if len(sys.argv)>1 else "output")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN and CHANNEL_ID):
    print("YouTube credentials missing in env. Skipping upload.")
    sys.exit(0)

def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    r.raise_for_status()
    return r.json()["access_token"]

def upload(file_path, title, desc, tags, made_for_kids=True, privacy="public", thumb=None):
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
    video_id = res["id"]
    print("Uploaded. video id:", video_id)
    if thumb and os.path.exists(thumb):
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb)).execute()
            print("Thumbnail uploaded for", video_id)
        except Exception as e:
            print("Thumbnail upload error:", e)
    return video_id

def main(out_folder):
    OUT = Path(out_folder)
    script = {}
    try:
        script = json.load(open(OUT/"script.json", encoding="utf-8"))
    except:
        script = {"title":"Animal Facts", "description":"Auto generated", "tags":[]}
    base_title = script.get("title","Animal Facts")
    desc = script.get("description","Auto generated animal facts video")
    if "Pexels" not in desc:
        desc = desc + "\n\nVideos source: Pexels (royalty-free)"
    tags = script.get("tags", [])
    # main info video
    for video in sorted(OUT.glob(f"final_*{script.get('animal_key','')}*")):
        title = base_title + " (Info)"
        thumb = Path("thumbnails") / f"{video.stem}.jpg"
        upload(str(video), title, desc, tags, made_for_kids=False, privacy="public", thumb=str(thumb) if thumb.exists() else None)
    # ambient videos
    for video in sorted(OUT.glob(f"ambient_*{script.get('animal_key','')}*")):
        title = base_title + " - Relaxing Clips"
        thumb = Path("thumbnails") / f"{video.stem}.jpg"
        upload(str(video), title, desc + "\nAmbient video (no narration).", tags, made_for_kids=False, privacy="public", thumb=str(thumb) if thumb.exists() else None)

if __name__ == "__main__":
    out_folder = sys.argv[1] if len(sys.argv)>1 else "output"
    main(out_folder)
