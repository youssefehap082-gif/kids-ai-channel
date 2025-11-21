import os
import json

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
    print("🚀 Starting Empire Construction...")
    
    # Create Structure
    base_dirs = [
        f"{PROJECT_NAME}/.github/workflows",
        f"{PROJECT_NAME}/config",
        f"{PROJECT_NAME}/scripts",
        f"{PROJECT_NAME}/utils",
        f"{PROJECT_NAME}/assets/temp",
        f"{PROJECT_NAME}/logs",
    ]
    for d in base_dirs: create_folder(d)

    # 1. Config: Animals List
    animals_list = {
        "strategy": "focus_cute_first",
        "categories": {
            "cute": ["Red Panda", "Quokka", "Sea Otter", "Capybara"],
            "predators": ["Lion", "Tiger", "Great White Shark"],
            "sea": ["Octopus", "Blue Whale"]
        }
    }
    create_file(f"{PROJECT_NAME}/config/animals_list.json", json.dumps(animals_list, indent=4))

    # 2. Config: Settings
    settings = {
        "video": {"resolution": "1080p", "shorts_daily": 5},
        "apis": {"tts": ["elevenlabs", "openai"], "stock": ["pexels", "pixabay"]}
    }
    create_file(f"{PROJECT_NAME}/config/settings.json", json.dumps(settings, indent=4))

    # 3. GitHub Actions Workflow
    workflow = """name: Daily Auto-Tube Pipeline

on:
  schedule:
    - cron: '0 11 * * *'
  workflow_dispatch:

jobs:
  produce_and_upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Dependencies
        run: pip install moviepy openai google-api-python-client requests cloudinary elevenlabs
      
      - name: Run Pipeline
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
        run: python scripts/main_pipeline.py
"""
    create_file(f"{PROJECT_NAME}/.github/workflows/daily_video.yml", workflow)

    # 4. Main Pipeline Script
    pipeline_code = """
import os
def run_pipeline():
    print("🎬 Starting Pipeline...")
    # Here we will add the full logic later
    print("✅ Done.")
if __name__ == "__main__":
    run_pipeline()
"""
    create_file(f"{PROJECT_NAME}/scripts/main_pipeline.py", pipeline_code)

    # 5. Requirements
    reqs = "moviepy==1.0.3\nopenai\ngoogle-api-python-client\nrequests\ncloudinary\nelevenlabs"
    create_file(f"{PROJECT_NAME}/requirements.txt", reqs)

    print(f"\n🎉 EMPIRE BUILT inside {PROJECT_NAME}!")

if __name__ == "__main__":
    main()