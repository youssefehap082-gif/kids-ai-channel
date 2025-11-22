import os

# ==========================================
# FIX: ADD WIKIPEDIA TO INSTALL LIST
# ==========================================

PROJECT_NAME = "." 

def create_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Fixed: {path}")

def main():
    print("🚀 FIXING WORKFLOW DEPENDENCIES...")

    # تحديث ملف GitHub Actions لإضافة wikipedia
    workflow = """name: Daily Auto-Tube Pipeline

on:
  schedule:
    - cron: '0 12 * * *'
    - cron: '0 16 * * *'
    - cron: '0 20 * * *'
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  produce_and_upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install System Deps
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg imagemagick ghostscript
          
      - name: Install Python Deps
        # التعديل هنا: تأكدنا من وجود wikipedia و edge-tts
        run: pip install openai requests google-api-python-client google-auth-oauthlib moviepy==1.0.3 imageio-ffmpeg gTTS edge-tts wikipedia Pillow

      - name: Run Pipeline
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
          YOUTUBE_CLIENT_ID: ${{ secrets.YT_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YT_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YT_REFRESH_TOKEN }}
        run: python scripts/main_pipeline.py
"""
    create_file(".github/workflows/daily_video.yml", workflow)
    
    # تحديث requirements.txt بالمرة
    reqs = """
moviepy==1.0.3
requests
google-api-python-client
google-auth-oauthlib
gTTS
imageio-ffmpeg
Pillow
edge-tts
wikipedia
"""
    create_file("requirements.txt", reqs)

    print("\n✅ FIX APPLIED: Wikipedia library added to installation list.")

if __name__ == "__main__":
    main()
