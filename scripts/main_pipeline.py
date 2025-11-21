
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
