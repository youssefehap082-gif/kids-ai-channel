import os
import json

# ==========================================
# PROJECT STRUCTURE BUILDER (UPDATED FOR USER SECRETS)
# ==========================================

PROJECT_NAME = "AutoAnimals_Empire"

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Created folder: {path}")

def create_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Created file: {path}")

def main():
    print("🚀 Starting Empire Construction (Customized for your Keys)...")
    
    # 1. Create Directory Structure
    base_dirs = [
        f"{PROJECT_NAME}/.github/workflows",
        f"{PROJECT_NAME}/config",
        f"{PROJECT_NAME}/scripts",
        f"{PROJECT_NAME}/utils",
        f"{PROJECT_NAME}/assets/temp",
        f"{PROJECT_NAME}/logs",
    ]
    
    for d in base_dirs:
        create_folder(d)

    # 2. Config Files
    animals_list = {
        "strategy": "focus_cute_first",
        "categories": {
            "cute": ["Red Panda", "Quokka", "Sea Otter", "Capybara"],
            "predators": ["Lion", "Tiger", "Great White Shark"],
            "sea": ["Octopus", "Blue Whale"]
        }
    }
    create_file(f"{PROJECT_NAME}/config/animals_list.json", json.dumps(animals_list, indent=4))

    settings = {
        "video": {"resolution": "1080p", "shorts_daily": 5},
        "apis": {"tts": ["elevenlabs", "openai"], "stock": ["pexels", "pixabay"]}
    }
    create_file(f"{PROJECT_NAME}/config/settings.json", json.dumps(settings, indent=4))

    # ==========================================
    # 3. GITHUB ACTIONS (MAPPED TO YOUR SECRETS)
    # ==========================================
    # Notice: We map YOUR secret names (right) to Script variables (left)
    github_workflow = """name: Daily Auto-Tube Pipeline

on:
  schedule:
    - cron: '0 11 * * *' # 7 AM EST
  workflow_dispatch: # Manual Trigger

jobs:
  produce_and_upload:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          sudo apt-get install -y ffmpeg imagemagick
          pip install -r requirements.txt

      - name: Run Fail-Proof Pipeline
        env:
          # --- MAPPING YOUR SECRETS TO SCRIPT VARIABLES ---
          # AI & TTS
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ELEVENLABS_API_KEY: ${{ secrets.ELEVEN_API_KEY }}  # Mapped
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          
          # STOCK MEDIA
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
          COVERR_API_KEY: ${{ secrets.COVERR_API_KEY }}
          STORYBLOCKS_API_KEY: ${{ secrets.STORYBLOCKS_API_KEY }}
          VECTEEZY_API_KEY: ${{ secrets.VECTEEZY_API_KEY }}
          
          # YOUTUBE AUTH
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YT_CLIENT_SECRET }} # Mapped
          YOUTUBE_CLIENT_ID: ${{ secrets.YT_CLIENT_ID }}         # Mapped
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YT_REFRESH_TOKEN }} # Mapped
          YOUTUBE_CHANNEL_ID: ${{ secrets.YT_CHANNEL_ID }}       # Mapped
          
          # CLOUD STORAGE
          CLOUDINARY_API_KEY: ${{ secrets.CLOUDINARY_API_KEY }}
          
        run: python scripts/main_pipeline.py
      
      - name: Upload Logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: run-logs
          path: logs/
"""
    create_file(f"{PROJECT_NAME}/.github/workflows/daily_video.yml", github_workflow)

    # 4. Main Pipeline Script (Updated to check keys)
    pipeline_code = """
import os
import sys

def check_keys():
    print("🔍 Checking System Fuel (API Keys)...")
    
    required_keys = [
        "OPENAI_API_KEY", 
        "ELEVENLABS_API_KEY", 
        "YOUTUBE_CLIENT_SECRET",
        "YOUTUBE_REFRESH_TOKEN"
    ]
    
    missing = []
    for key in required_keys:
        if not os.environ.get(key):
            missing.append(key)
            
    if missing:
        print(f"❌ CRITICAL ERROR: Missing Keys: {missing}")
        print("⚠️  Please check GitHub Secrets mapping.")
        # We don't exit yet to allow partial runs in future
    else:
        print("✅ All Core Keys Detected. Systems Online.")

def run_pipeline():
    print("🎬 Starting Daily Auto-Tube Pipeline...")
    check_keys()
    
    # Placeholder for Phase 2 Logic
    print("ℹ️  Pipeline is ready for Phase 2 (Content Generation).")
    print("✅ Execution finished.")

if __name__ == "__main__":
    run_pipeline()
"""
    create_file(f"{PROJECT_NAME}/scripts/main_pipeline.py", pipeline_code)

    # 5. Requirements
    requirements = """
moviepy==1.0.3
openai
google-api-python-client
google-auth-oauthlib
google-auth-httplib2
requests
cloudinary
elevenlabs
pillow
numpy
pandas
"""
    create_file(f"{PROJECT_NAME}/requirements.txt", requirements)

    print(f"\n🎉 EMPIRE UPDATED! Mapped to YOUR keys inside {PROJECT_NAME}")

if __name__ == "__main__":
    main()