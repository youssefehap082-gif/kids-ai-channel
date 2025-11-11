import os, sys, time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

YT_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]  # لا نغيّر السكوب عشان الريفريش توكن الحالي

def get_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        scopes=YT_SCOPE,
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def _log_channel_hint(youtube):
    # معلومات إرشادية (لو السكوب مش مكفي مش هنعطل الرفع)
    try:
        ch = youtube.channels().list(part="id,snippet", mine=True).execute()
        if ch.get("items"):
            c = ch["items"][0]
            print(f"📺 Uploading to channel: {c['snippet']['title']} (ID: {c['id']})")
        else:
            print("⚠️ Could not read channel info (no items).")
    except Exception as e:
        print(f"⚠️ Channel info not available (scope/read issue): {e}")

def upload_video(file_path, title, description, tags, privacy="public", schedule_time_rfc3339=None):
    youtube = get_service()
    _log_channel_hint(youtube)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "15",  # Animals
        },
        "status": {"privacyStatus": privacy},
    }
    if schedule_time_rfc3339:
        body["status"]["publishAt"] = schedule_time_rfc3339
        body["status"]["privacyStatus"] = "private"

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"🚀 Starting YouTube upload: {title}")
    response = None
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"📦 Uploading... {int(status.progress() * 100)}%")
    except Exception as e:
        print(f"❌ Upload error: {e}")
        sys.exit(1)

    if not isinstance(response, dict) or "id" not in response:
        print("❌ Upload failed - no video ID returned.")
        sys.exit(1)

    vid = response["id"]
    print(f"✅ Uploaded! Video ID: {vid}")
    print(f"🔗 Watch URL: https://www.youtube.com/watch?v={vid}")
    print(f"🎬 Studio URL: https://studio.youtube.com/video/{vid}/edit")

    # محاولة تحقّق خفيفة (لو السكوب مش مكفي مش نكسر الرفع)
    try:
        info = youtube.videos().list(part="status", id=vid).execute()
        if not info.get("items"):
            print("⚠️ Could not verify video by API (no items), but YouTube returned an ID.")
        else:
            vis = info["items"][0]["status"]["privacyStatus"]
            print(f"👁️ Visibility on YouTube: {vis}")
    except Exception as e:
        print(f"⚠️ Verification call failed (scope/permission): {e}")

    return vid
