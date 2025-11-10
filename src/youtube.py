import os, time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

def _client():
    creds = Credentials(
        None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    return build("youtube","v3",credentials=creds,cache_discovery=False)

def upload_video(video_path, title, desc, tags, thumb_path=None, privacy="public"):
    yt = _client()
    body = {
        "snippet":{"title":title[:100], "description":desc[:4800], "tags":tags[:500], "categoryId":"15"},
        "status":{"privacyStatus":privacy}
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response=None
    while response is None:
        status, response = req.next_chunk()
        if status: print(f"⬆️ Uploading... {int(status.progress()*100)}%")
    vid = response["id"]
    print(f"✅ Uploaded: https://youtu.be/{vid}")

    if thumb_path:
        try:
            yt.thumbnails().set(videoId=vid, media_body=thumb_path).execute()
            print("🖼️ Thumbnail set.")
        except Exception as e:
            print(f"⚠️ Thumbnail failed: {e}")

    # Auto comment
    try:
        yt.commentThreads().insert(part="snippet", body={
            "snippet": {
                "videoId": vid,
                "topLevelComment":{"snippet":{"textOriginal":"Which animal do you want next? 🐾 Comment below!"}}
            }
        }).execute()
        print("💬 Auto comment posted.")
    except Exception as e:
        print(f"⚠️ Comment failed: {e}")

    return vid

def get_video_stats(video_id: str) -> int:
    yt = _client()
    r = yt.videos().list(part="statistics", id=video_id).execute()
    items = r.get("items",[])
    if not items: return 0
    return int(items[0]["statistics"].get("viewCount","0"))

def list_recent_videos(limit=50):
    """يرجع قائمة أحدث فيديوهات القناة (id, title, is_short)."""
    yt = _client()
    cid_resp = yt.channels().list(part="id", mine=True).execute()
    ch_id = cid_resp["items"][0]["id"]
    search = yt.search().list(part="id,snippet", channelId=ch_id, maxResults=min(50,limit), order="date").execute()
    results=[]
    for it in search.get("items", []):
        vid = it["id"].get("videoId")
        if not vid: continue
        title = it["snippet"].get("title","")
        # shorts detection (تقريبي)
        is_short = "#shorts" in title.lower()
        results.append({"id": vid, "title": title, "is_short": is_short})
    return results

def get_video_stats_bulk(ids):
    """يرجع {id: {views, likes}} لدفعة IDs."""
    out = {}
    if not ids: return out
    yt = _client()
    for i in range(0, len(ids), 50):
        chunk = ids[i:i+50]
        r = yt.videos().list(part="statistics", id=",".join(chunk)).execute()
        for it in r.get("items", []):
            s = it.get("statistics", {})
            out[it["id"]] = {
                "views": int(s.get("viewCount","0")),
                "likes": int(s.get("likeCount","0")) if "likeCount" in s else 0
            }
    return out
