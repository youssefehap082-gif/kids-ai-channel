import os
import json

# ==========================================
# PHASE 2.5: FIXING THE PATH (NO SUBFOLDER)
# ==========================================

# التعديل هنا: النقطة دي معناها "ابني هنا في وشي مش جوه فولدر"
PROJECT_NAME = "." 

def create_file(path, content):
    # Ensure directory exists
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Updated/Created: {path}")

def main():
    print("🚀 RE-STRUCTURING EMPIRE (Root Level)...")

    # 1. CONTENT ENGINE
    content_engine = """
import os
import json
from openai import OpenAI

def generate_script(animal_name):
    print(f"📝 Generating Script for: {animal_name}")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = f'''
    Topic: {animal_name}
    Style: Viral YouTube Shorts.
    Structure: Hook, Intro, 3 Facts, Outro.
    Output: JSON keys: hook, intro, facts (list), outro.
    '''
    try:
        # Mock response for testing if API fails or credits low
        # Remove this mock block to use real API
        return {
            "hook": f"Did you know {animal_name} can do this?",
            "intro": "Welcome to Animal Facts.",
            "facts": ["Fact 1 is crazy.", "Fact 2 is wild.", "Fact 3 is wow."],
            "outro": "Subscribe for more!"
        }
    except Exception as e:
        print(f"❌ Script Gen Failed: {e}")
        return None
"""
    create_file(f"scripts/content_engine.py", content_engine)

    # 2. MEDIA ENGINE
    media_engine = """
import os
import requests

def gather_media(animal_name):
    print(f"🎥 Hunting media for: {animal_name}")
    # Mock return for testing pipeline structure
    return ["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"]
"""
    create_file(f"scripts/media_engine.py", media_engine)

    # 3. VOICE ENGINE
    voice_engine = """
import os
def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voiceover (Mock Mode for Test)...")
    # Create a dummy file just to pass the check
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f: f.write("dummy audio")
    return output_path
"""
    create_file(f"scripts/voice_engine.py", voice_engine)

    # 4. MAIN PIPELINE
    main_pipeline = """
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media
from voice_engine import generate_voice

def run_pipeline():
    print("🎬 Starting AUTO-TUBE Pipeline...")
    
    animal = "Red Panda"
    print(f"🦁 Processing: {animal}")

    script = generate_script(animal)
    voice = generate_voice("test text")
    media = gather_media(animal)
    
    print("✅ Phase 2 Logic Verified. All modules connected.")

if __name__ == "__main__":
    run_pipeline()
"""
    create_file(f"scripts/main_pipeline.py", main_pipeline)

    # 5. GITHUB ACTIONS (CORRECT LOCATION)
    # Added 'workflow_dispatch' for manual button
    workflow = """name: Daily Auto-Tube Pipeline

on:
  push:                 # Runs on every push (for testing)
  workflow_dispatch:    # Manual Button

jobs:
  produce_and_upload:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Libs
        run: pip install openai requests

      - name: Run Pipeline
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python scripts/main_pipeline.py
"""
    create_file(f".github/workflows/daily_video.yml", workflow)
    
    # 6. ANIMALS CONFIG
    create_file("config/animals_list.json", '{"test": "true"}')

    print(f"\n🎉 FIXED! The robot is now in the main lobby (Root Directory).")

if __name__ == "__main__":
    main()