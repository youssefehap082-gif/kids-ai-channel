
import os
import sys
import json

# Add script dir to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media
from voice_engine import generate_voice

def run_pipeline():
    print("🎬 Starting AUTO-TUBE Production Engine...")
    
    # 1. Pick Topic (Simple rotation for now)
    try:
        with open('config/animals_list.json', 'r') as f:
            data = json.load(f)
            # For demo: Pick first cute animal
            animal = data['categories']['cute'][0] 
    except:
        animal = "Red Panda"

    print(f"🦁 Today's Star: {animal}")

    # 2. Generate Script
    script_data = generate_script(animal)
    if not script_data:
        print("❌ Critical: Script failed.")
        return

    # Combine text for TTS
    full_text = f"{script_data['hook']} {script_data['intro']} " + " ".join(script_data['facts']) + f" {script_data['outro']}"
    
    # 3. Generate Voice
    audio_path = generate_voice(full_text)
    if not audio_path:
        print("❌ Critical: Voice failed.")
        return

    # 4. Gather Media
    video_clips = gather_media(animal)
    if not video_clips:
        print("❌ Critical: No Media found.")
        return
        
    # 5. Save Metadata for Editing Phase
    meta = {
        "animal": animal,
        "script": script_data,
        "audio_path": audio_path,
        "video_urls": video_clips
    }
    with open("assets/temp/metadata.json", "w") as f:
        json.dump(meta, f, indent=4)
        
    print("✅ Phase 2 Complete: Assets Ready for Editing.")

if __name__ == "__main__":
    run_pipeline()
