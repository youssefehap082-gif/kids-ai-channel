#!/usr/bin/env python3
# scripts/upload_youtube.py
import os, sys, time, json
from pathlib import Path
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def log(*args, **kwargs):
    print(*args, **kwargs, flush=True)

CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")
CHANNEL_ID = os.environ.get("YT_CHANNEL_ID")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN and CHANNEL_ID):
    log("[ERROR] Missing one or more YouTube env vars (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, YT_CHANNEL_ID). Exiting.")
    sys.exit(1)

def get_access_token(client_id, client_secret, refresh_token):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    r = requests.post(token_url, data=data, timeout=30)
    log("[DEBUG] token endpoint status:", r.status_code)
    r.raise_for_status()
    j = r.json()
    return j.get("access_token"), j.get("expires_in")

def build_youtube_client(access_token):
    creds = Credentials(token=access_token, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    return youtube

def resumable_upload(youtube, file_path, title, description, tags, made_for_kids=False, privacy="public"):
    body = {
        "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "22"},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": made_for_kids}
    }
    log(f"[UPLOAD] {file_path}")
    media = MediaFileUpload(str(file_path), chunksize=1024*1024, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    retry = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                log(f"[UPLOAD] progress {int(status.progress()*100)}%")
        except Exception as e:
            retry += 1
            log(f"[WARN] upload chunk error (attempt {retry}): {e}")
            if retry > 5:
                log("[ERROR] too many upload errors.")
                raise
            time.sleep(2 ** retry)
    log("[OK] uploaded id:", response.get("id"))
    return response.get("id")

def set_thumbnail(youtube, video_id, thumb_path):
    try:
        if not Path(thumb_path).exists():
            log("[WARN] thumbnail not found:", thumb_path)
            return False
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb_path))).execute()
        log("[OK] thumbnail set")
        return True
    except Exception as e:
        log("[ERROR] thumbnail upload failed:", e)
        return False

def main(out_folder):
    OUT = Path(out_folder)
    manifest_path = OUT / ".build_manifest.json"
    files_to_upload = []
    if manifest_path.exists():
        try:
            mf = json.load(open(manifest_path, encoding="utf-8"))
            files_to_upload = [OUT / f for f in mf.get("files", []) if (OUT / f).exists()]
            log("[INFO] Using manifest files:", files_to_upload)
        except Exception as e:
            log("[WARN] Failed to read manifest:", e)

    if not files_to_upload:
        # fallback: glob patterns
        patterns = ["final_*.mp4", "ambient_*.mp4", "short_*.mp4"]
        for p in patterns:
            files_to_upload += sorted(list(OUT.glob(p)))
        log("[INFO] Fallback files:", [str(p) for p in files_to_upload])

    if not files_to_upload:
        log("[ERROR] No video files found in", OUT, ". Nothing to upload.")
        sys.exit(1)

    # read SEO from script.json if possible
    script = {}
    try:
        script = json.load(open(OUT/"script.json", encoding="utf-8"))
    except:
        script = {}
    base_title = script.get("title","Animal Facts")
    description = script.get("description","Auto generated animal facts video")
    if "Pexels" not in description:
        description = description + "\n\nVideos source: Pexels (royalty-free)"
    tags = script.get("tags", [])

    # get token + client
    access_token, expires_in = get_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
    if not access_token:
        log("[ERROR] Could not obtain access token.")
        sys.exit(1)
    youtube = build_youtube_client(access_token)
    uploaded = []
    for f in files_to_upload:
        try:
            name = f.name
            if name.startswith("final_") and "info" in name:
                title = base_title + " (Info)"
            elif name.startswith("final_"):
                title = base_title + " (Info)"
            elif name.startswith("ambient_"):
                title = base_title + " — Relaxing Clips"
            else:
                title = base_title
            vidid = resumable_upload(youtube, f, title, description, tags, made_for_kids=False, privacy="public")
            # thumbnail
            thumb = Path("thumbnails") / f"{f.stem}.jpg"
            if thumb.exists():
                set_thumbnail(youtube, vidid, thumb)
            uploaded.append((f.name, vidid))
        except Exception as e:
            log("[ERROR] upload failed for", f, e)

    log("[DONE] Uploaded:", uploaded)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv)>1 else "output"
    main(out)
