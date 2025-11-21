
import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

def upload_video(file_path, title, description):
    print("🚀 Uploading to YouTube...")
    
    # Reconstruct Credentials from Secrets
    token_info = {
        "client_id": os.environ.get("YOUTUBE_CLIENT_ID"),
        "client_secret": os.environ.get("YOUTUBE_CLIENT_SECRET"),
        "refresh_token": os.environ.get("YOUTUBE_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    
    if not all(token_info.values()):
        print("❌ Missing YouTube Keys")
        return None

    try:
        creds = Credentials.from_authorized_user_info(token_info)
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["shorts", "animals", "nature"],
                    "categoryId": "15" # Pets & Animals
                },
                "status": {
                    "privacyStatus": "public", # Changed to PUBLIC for action
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=googleapiclient.http.MediaFileUpload(file_path)
        )
        response = request.execute()
        print(f"✅ Upload Success! Video ID: {response['id']}")
        return response['id']
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        return None
