#!/usr/bin/env python3
# scripts/upload_youtube.py
import os, json, time
from pathlib import Path

OUT = Path("output")
if not OUT.exists():
    print("output/ missing")
    raise SystemExit(1)

MANIFEST = OUT / ".build_manifest.json"
if not MANIFEST.exists():
    print(".build_manifest.json not found")
    raise SystemExit(1)

data = json.load(open(MANIFEST, encoding="utf-8"))
files = data.get("files", [])
title = data.get("title") or (files[0] if files else "Auto Video")
description = data.get("description","")
tags = data.get("tags",[])

# YouTube OAuth secrets from env
CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")
CHANNEL_ID = os.environ.get("YT_CHANNEL_ID")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN and CHANNEL_ID):
    print("Missing YouTube secrets. Skipping upload.")
    raise SystemExit(1)

# exchange refresh token for access token using google-auth library
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

creds = Credentials(token=None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube"])
try:
    creds.refresh(Request())
except Exception as e:
    print("Failed to refresh credentials:", e)
    raise SystemExit(1)

yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

def upload_video(file_path, title, description, tags, privacy="public"):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "28"  # Science & Technology (change if you want)
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True, mimetype="video/*")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    print("Starting upload:", file_path.name)
    res = None
    try:
        res = req.execute()
        print("Upload finished. Video id:", res.get("id"))
        return res.get("id")
    except Exception as e:
        print("Upload error:", e)
        raise

# upload thumbnail if exists
def set_thumbnail(video_id, thumb_path):
    try:
        req = yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb_path)))
        r = req.execute()
        print("Thumbnail set:", r)
    except Exception as e:
        print("Thumbnail error:", e)

uploaded = []
for f in files:
    fp = OUT / f
    if not fp.exists():
        print("Missing file:", fp)
        continue
    vid_id = upload_video(fp, title, description, tags, privacy="public")
    uploaded.append(vid_id)
    thumb = OUT / "thumbnail.jpg"
    if thumb.exists():
        set_thumbnail(vid_id, thumb)
    # add a small delay
    time.sleep(2)

print("Uploaded video ids:", uploaded)
