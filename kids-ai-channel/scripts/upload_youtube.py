import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video(file_path, meta_data, is_short=False):
    # This requires valid OAuth2 tokens saved in secrets
    # Mock implementation for pipeline structure
    
    print(f"Mock Uploading {file_path} to YouTube...")
    print(f"Title: {meta_data['title']}")
    print(f"Tags: {meta_data['hashtags']}")
    
    # Update history
    _log_upload(file_path)

def _log_upload(path):
    log_file = "data/upload_history.json"
    history = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            history = json.load(f)
    
    history.append({"path": path, "status": "uploaded"})
    
    with open(log_file, 'w') as f:
        json.dump(history, f)
