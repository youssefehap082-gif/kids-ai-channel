#!/usr/bin/env python3
# scripts/upload_youtube.py
import os, sys, json, time, requests
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

OUT = Path(sys.argv[1] if len(sys.argv)>1 else "output")

CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")
CHANNEL_ID = os.environ.get("YT_CHANNEL_ID")

def log(*a, **k):
    print(*a, **k, flush=True)

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN and CHANNEL_ID):
    log("[ERROR] Missing YouTube secrets. Skipping upload.")
    sys.exit(1)

def get_access_token(cid,csec,rt):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": cid,
        "client_secret": csec,
        "refresh_token": rt,
        "grant_type": "refresh_token"
    }, timeout=30)
    log("[DEBUG] token status", r.status_code)
    r.raise_for_status()
    return r.json().get("access_token")

def build_client(token):
    creds = Credentials(token=token, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    youtube = build("youtube","v3", credentials=creds, cache_discovery=False)
    return youtube

def resumable_upload(youtube, file_path, title, desc, tags):
    body = {"snippet":{"title":title,"description":desc,"tags":tags,"categoryId":"22"},"status":{"privacyStatus":"public","selfDeclaredMadeForKids":False}}
    media = MediaFileUpload(str(file_path), chunksize=1024*1024, resumable=True, mimetype="video/*")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            log("upload progress", int(status.progress()*100))
    return response.get("id")

def set_thumb(youtube, vidid, thumb_path):
    try:
        if thumb_path.exists():
            youtube.thumbnails().set(videoId=vidid, media_body=MediaFileUpload(str(thumb_path))).execute()
            log("Thumbnail set for", vidid)
    except Exception as e:
        log("Thumb upload error:", e)

# Prepare files to upload: use manifest if exists else patterns
files = []
manifest = OUT / ".build_manifest.json"
if manifest.exists():
    try:
        mf = json.load(manifest.open(encoding="utf-8"))
        files = [OUT / f for f in mf.get("files", []) if (OUT / f).exists()]
    except:
        files = []
if not files:
    # fallback patterns
    for pat in ["final_*.mp4","ambient_*.mp4","short_*.mp4"]:
        files += sorted(list(OUT.glob(pat)))
log = print

if not files:
    log("[ERROR] No video files found in output. Nothing to upload.")
    sys.exit(1)

token = get_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
youtube = build_client(token)
log("[INFO] Uploading files:", [p.name for p in files])

# read script for SEO
script = {}
try:
    script = json.load(open(OUT/"script.json", encoding="utf-8"))
except: script = {}
base_title = script.get("title","Animal Facts")
desc = script.get("description","Auto generated")
tags = script.get("tags",[])

for f in files:
    try:
        # decide title
        if "final_" in f.name and "info" in f.name:
            title = base_title + " (Info)"
        elif "ambient_" in f.name:
            title = base_title + " — Relaxing Clips"
        else:
            title = base_title
        vidid = resumable_upload(youtube, f, title, desc, tags)
        thumb = Path("thumbnails") / f"{f.stem}.jpg"
        set_thumb(youtube, vidid, thumb)
        log("[OK] Uploaded", f.name, "->", vidid)
    except Exception as e:
        log("[ERROR] upload failed for", f.name, e)
