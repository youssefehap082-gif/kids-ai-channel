#!/usr/bin/env python3
# scripts/upload_youtube.py
# Robust YouTube uploader using refresh token -> access token -> googleapiclient
# Expects env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, YT_CHANNEL_ID
# Usage: python3 scripts/upload_youtube.py output

import os
import sys
import time
import json
import requests
from pathlib import Path

# google client libs
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ---------- helpers ----------
def log(*args, **kwargs):
    print(*args, **kwargs, flush=True)

def get_env(name):
    v = os.environ.get(name)
    if not v:
        log(f"[ERROR] Missing env: {name}")
    return v

# ---------- token handling ----------
def get_access_token(client_id, client_secret, refresh_token):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    try:
        r = requests.post(token_url, data=data, timeout=30)
        log("[DEBUG] token endpoint status:", r.status_code)
        r.raise_for_status()
        j = r.json()
        access_token = j.get("access_token")
        expires_in = j.get("expires_in")
        if not access_token:
            log("[ERROR] No access_token in token response:", j)
            return None, None
        log("[OK] Obtained access_token (expires_in={}s)".format(expires_in))
        return access_token, expires_in
    except Exception as e:
        log("[ERROR] Failed to get access token:", e)
        try:
            log("Response text:", r.text[:500])
        except:
            pass
        return None, None

# ---------- uploader ----------
def build_youtube_client(access_token, refresh_token, client_id, client_secret):
    # Build Credentials object with token + client info so googleapiclient can refresh if needed
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    return youtube

def resumable_upload(youtube, file_path, title, description, tags, categoryId="22", privacy="public", made_for_kids=False):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": categoryId
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": made_for_kids
        }
    }
    log(f"[UPLOAD] Preparing upload: {file_path} (size={file_path.stat().st_size} bytes)")
    media = MediaFileUpload(str(file_path), chunksize=1024*1024, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    retry = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                log(f"[UPLOAD] Upload progress: {pct}%")
        except Exception as e:
            retry += 1
            log(f"[WARN] upload chunk error (attempt {retry}):", e)
            if retry > 5:
                log("[ERROR] Too many upload errors. Aborting upload.")
                raise
            time.sleep(2 ** retry)
    log("[OK] Upload finished. got response id:", response.get("id"))
    return response.get("id")

def set_thumbnail(youtube, video_id, thumb_path):
    try:
        if not thumb_path.exists():
            log("[WARN] thumbnail not found:", str(thumb_path))
            return False
        log("[THUMB] Uploading thumbnail:", thumb_path)
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb_path))).execute()
        log("[OK] Thumbnail uploaded.")
        return True
    except Exception as e:
        log("[ERROR] Thumbnail upload failed:", e)
        return False

# ---------- main ----------
def main():
    CLIENT_ID = get_env("YT_CLIENT_ID")
    CLIENT_SECRET = get_env("YT_CLIENT_SECRET")
    REFRESH_TOKEN = get_env("YT_REFRESH_TOKEN")
    CHANNEL_ID = get_env("YT_CHANNEL_ID")

    if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN and CHANNEL_ID):
        log("[ERROR] Missing one or more YouTube secrets. Aborting upload step.")
        return 1

    out_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output")
    if not out_folder.exists():
        log("[ERROR] Output folder not found:", out_folder)
        return 1

    # read script.json for SEO, but fallback OK
    script_json_path = out_folder / "script.json"
    script = {}
    if script_json_path.exists():
        try:
            script = json.load(open(script_json_path, encoding="utf-8"))
        except Exception as e:
            log("[WARN] Failed to parse script.json:", e)

    title_base = script.get("title", "Animal Facts")
    description = script.get("description", "")
    if "Pexels" not in description:
        description = description + "\n\nVideos source: Pexels (royalty-free)"

    tags = script.get("tags", []) if isinstance(script.get("tags", []), list) else []

    # find candidate files
    final_videos = sorted(list(out_folder.glob("final_*.mp4")) + list(out_folder.glob("ambient_*.mp4")) + list(out_folder.glob("short_*.mp4")))
    if not final_videos:
        log("[ERROR] No video files found in", out_folder, ". Nothing to upload.")
        return 1

    log("[INFO] Videos to upload:", [p.name for p in final_videos])

    # get fresh access token
    access_token, expires_in = get_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
    if not access_token:
        log("[ERROR] Could not obtain access token. Check refresh token and client credentials.")
        return 1

    # build client
    youtube = build_youtube_client(access_token, REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET)
    log("[OK] YouTube client built. Starting uploads...")

    uploaded_ids = []
    for vid in final_videos:
        try:
            # decide title variations
            if "final_" in vid.name and "info" in vid.name:
                t = title_base + " (Info)"
            elif "final_" in vid.name:
                t = title_base + " (Info)"
            elif "ambient_" in vid.name:
                t = title_base + " — Relaxing Clips"
            else:
                t = title_base

            # for shorts maybe adjust privacy or tags
            video_id = resumable_upload(youtube, vid, t, description, tags, privacy="public", made_for_kids=False)
            uploaded_ids.append((vid.name, video_id))

            # set thumbnail if exists
            thumb_candidate = Path("thumbnails") / f"{vid.stem}.jpg"
            if thumb_candidate.exists():
                set_thumbnail(youtube, video_id, thumb_candidate)
            else:
                log("[WARN] thumbnail not found for", vid.name)
        except Exception as e:
            log("[ERROR] Upload failed for", vid.name, ":", e)

    log("[DONE] Uploaded videos (name -> videoId):")
    for n, vidid in uploaded_ids:
        log(" -", n, "->", vidid)

    return 0

if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
