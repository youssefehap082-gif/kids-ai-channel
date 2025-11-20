import os
import time
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Setup logging
logging.basicConfig(level=logging.INFO)

def upload_video(file_path, meta_data, is_short=False):
    logging.info(f"Preparing to upload: {file_path}")

    # 1. Get Credentials from Environment Variables
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        logging.error("Missing YouTube Credentials! Check GitHub Secrets.")
        return

    try:
        # 2. Authenticate
        creds = Credentials(
            None, # Access token will be refreshed automatically
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )

        youtube = build("youtube", "v3", credentials=creds)

        # 3. Prepare Metadata
        title = meta_data.get("title", "Amazing Animal Fact")
        description = meta_data.get("description", "Subscribe for more!")
        tags = meta_data.get("hashtags", ["animals", "shorts"])

        if is_short:
            title = title + " #Shorts"
            description = description + "\n#Shorts #Animals"

        # Truncate title if too long (YouTube limit is 100)
        if len(title) > 100:
            title = title[:97] + "..."

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "15" # Category 15 is "Pets & Animals"
            },
            "status": {
                "privacyStatus": "public", # Change to 'private' if you want to review first
                "selfDeclaredMadeForKids": False
            }
        }

        # 4. Upload File
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        
        logging.info("Uploading to YouTube... Please wait.")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logging.info(f"Uploaded {int(status.progress() * 100)}%")

        logging.info(f"UPLOAD SUCCESS! Video ID: {response.get('id')}")
        logging.info(f"Link: https://youtu.be/{response.get('id')}")

    except Exception as e:
        logging.error(f"YouTube Upload Failed: {e}")
        import traceback
        traceback.print_exc()