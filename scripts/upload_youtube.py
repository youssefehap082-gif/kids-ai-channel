import os
import logging
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Setup logging to print to console visibly
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def upload_video(file_path, meta_data, is_short=False):
    print(f"\n========== STARTING UPLOAD FOR: {file_path} ==========")
    
    # 1. Check Credentials
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not client_id or not client_secret or not refresh_token:
        print("FATAL ERROR: One or more YouTube keys are missing in Secrets!")
        sys.exit(1) # Force Red X in GitHub

    try:
        # 2. Authenticate
        print("--> Authenticating with Google...")
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )
        
        youtube = build("youtube", "v3", credentials=creds)

        # 3. Prepare Data
        title = meta_data.get("title", "Amazing Animal Fact")
        if is_short: title += " #Shorts"
        if len(title) > 100: title = title[:99]

        body = {
            "snippet": {
                "title": title,
                "description": meta_data.get("description", "") + "\n#Animals",
                "tags": meta_data.get("hashtags", ["animals"]),
                "categoryId": "15"
            },
            "status": {
                "privacyStatus": "public", # Make sure it's public
                "selfDeclaredMadeForKids": False
            }
        }

        # 4. Upload
        print("--> Uploading file bytes...")
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"--> Uploading: {int(status.progress() * 100)}%")

        print("\n=============================================")
        print(f"SUCCESS! VIDEO UPLOADED.")
        print(f"URL: https://youtu.be/{response.get('id')}")
        print("=============================================\n")

    except Exception as e:
        # THIS IS THE IMPORTANT PART
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("YOUTUBE UPLOAD FAILED (GOOGLE REJECTED IT):")
        print(e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        # Force the pipeline to CRASH so you see a Red X
        sys.exit(1)