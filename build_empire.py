import os
import json

# ==========================================
# PHASE 2: BRAINS & MUSCLES UPDATE
# ==========================================

PROJECT_NAME = "AutoAnimals_Empire"

def create_file(path, content):
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Updated/Created: {path}")

def main():
    print("🚀 Injecting AI Logic into the Empire...")

    # 1. CONTENT ENGINE (The Writer)
    # Writes viral scripts using LLMs
    content_engine = """
import os
import json
import random
from openai import OpenAI

def generate_script(animal_name):
    print(f"📝 Generating Script for: {animal_name}")
    
    # Initialize Client (Standard OpenAI for now, easy to swap)
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f'''
    You are a YouTube scriptwriter for a viral animal channel.
    Topic: {animal_name}
    Style: Energetic, Mysterious, Fast-paced.
    Structure:
    1. Hook (0-5s): Shocking fact or question.
    2. Intro (5-15s): Quick intro.
    3. 5 Amazing Facts: Mix of scary/cute/bizarre.
    4. Conclusion: Call to action.
    
    Output format: JSON only with keys: "hook", "intro", "facts" (list of strings), "outro".
    '''
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        script_data = json.loads(response.choices[0].message.content)
        print("✅ Script Generated Successfully")
        return script_data
    except Exception as e:
        print(f"❌ Script Gen Failed: {e}")
        return None
"""
    create_file(f"{PROJECT_NAME}/scripts/content_engine.py", content_engine)

    # 2. MEDIA ENGINE (The Hunter)
    # Fetches Videos/Images from Pexels/Pixabay
    media_engine = """
import os
import requests
import random

def search_pexels(query, api_key, per_page=5):
    headers = {'Authorization': api_key}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&orientation=landscape"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return [v['video_files'][0]['link'] for v in r.json()['videos'] if v['video_files']]
    except:
        return []
    return []

def search_pixabay(query, api_key):
    url = f"https://pixabay.com/api/videos/?key={api_key}&q={query}&per_page=5"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return [v['videos']['large']['url'] for v in r.json()['hits']]
    except:
        return []
    return []

def gather_media(animal_name):
    print(f"🎥 Hunting media for: {animal_name}")
    
    pexels_key = os.environ.get("PEXELS_API_KEY")
    pixabay_key = os.environ.get("PIXABAY_API_KEY")
    
    videos = []
    
    # 1. Try Pexels
    if pexels_key:
        videos += search_pexels(animal_name, pexels_key)
        
    # 2. Try Pixabay (Fallback/Addition)
    if pixabay_key and len(videos) < 3:
        videos += search_pixabay(animal_name, pixabay_key)
    
    # Fallback: General animal query if specific fails
    if not videos:
        print("⚠️ Specific search failed, trying general tag...")
        if pexels_key: videos += search_pexels("wildlife", pexels_key)
        
    print(f"✅ Found {len(videos)} videos.")
    return videos[:5] # Return top 5
"""
    create_file(f"{PROJECT_NAME}/scripts/media_engine.py", media_engine)

    # 3. VOICE ENGINE (The Narrator)
    # ElevenLabs -> Fallback to OpenAI
    voice_engine = """
import os
import requests
from openai import OpenAI

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voiceover...")
    
    eleven_key = os.environ.get("ELEVENLABS_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    # 1. Try ElevenLabs (Best Quality)
    if eleven_key:
        try:
            # Adam Voice ID (Popular viral voice)
            voice_id = "pNInz6obpgDQGcFmaJgB" 
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
            r = requests.post(url, json=data, headers=headers)
            if r.status_code == 200:
                with open(output_path, 'wb') as f: f.write(r.content)
                print("✅ Voice generated (ElevenLabs)")
                return output_path
        except Exception as e:
            print(f"⚠️ ElevenLabs Failed: {e}")

    # 2. Fallback to OpenAI TTS
    if openai_key:
        try:
            client = OpenAI(api_key=openai_key)
            response = client.audio.speech.create(
                model="tts-1",
                voice="onyx", # Deep male voice
                input=text
            )
            response.stream_to_file(output_path)
            print("✅ Voice generated (OpenAI Fallback)")
            return output_path
        except Exception as e:
            print(f"❌ OpenAI TTS Failed: {e}")
            
    return None
"""
    create_file(f"{PROJECT_NAME}/scripts/voice_engine.py", voice_engine)

    # 4. MAIN PIPELINE (Updated Orchestrator)
    main_pipeline = """
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
"""
    create_file(f"{PROJECT_NAME}/scripts/main_pipeline.py", main_pipeline)

    print(f"\n🎉 LOGIC INJECTED! Your Empire now has a Brain.")

if __name__ == "__main__":
    main()