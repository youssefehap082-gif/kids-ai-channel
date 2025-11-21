import os
import json

# ==========================================
# PHASE 3.5: FREE MODE (NO OPENAI COST)
# ==========================================

PROJECT_NAME = "." 

def create_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Created: {path}")

def main():
    print("🚀 ACTIVATING FREE EMERGENCY ENGINES...")

    # 1. CONTENT ENGINE (TEMPLATE BASED - FREE)
    content_engine = """
import random

def generate_script(animal_name):
    print(f"📝 Writing Script using FREE Template for: {animal_name}")
    
    # Database of facts (Fallback system)
    facts_db = {
        "Red Panda": [
            "Red Pandas use their bushy tails as blankets in winter.",
            "They are the original Panda, discovered before the Giant Panda!",
            "They consume 200,000 bamboo leaves every day."
        ],
        "Lion": [
            "A lion's roar can be heard from 5 miles away.",
            "Lions sleep for up to 20 hours a day.",
            "Females do 90 percent of the hunting."
        ]
    }
    
    facts = facts_db.get(animal_name, [
        f"{animal_name} is an amazing creature.",
        f"Scientists are still discovering secrets about the {animal_name}.",
        "Nature is truly wonderful."
    ])
    
    script_text = f"Did you know these facts about the {animal_name}? {facts[0]} {facts[1]} {facts[2]} Subscribe for more animal facts!"
    
    return {
        "title": f"Shocking Facts about {animal_name} 😱 #shorts",
        "description": f"Amazing facts about {animal_name}. #shorts #animals #nature",
        "script_text": script_text
    }
"""
    create_file("scripts/content_engine.py", content_engine)

    # 2. VOICE ENGINE (GOOGLE TTS - FREE)
    voice_engine = """
from gtts import gTTS
import os

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voice using Google TTS (Free)...")
    try:
        # Create directory if not exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        
        print("✅ Voice Generated Successfully")
        return output_path
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None
"""
    create_file("scripts/voice_engine.py", voice_engine)

    # 3. UPDATE REQUIREMENTS (ADD gTTS)
    requirements = """
moviepy==1.0.3
requests
google-api-python-client
google-auth-oauthlib
gTTS
imageio-ffmpeg
"""
    create_file("requirements.txt", requirements)

    print("\n✅ FREE ENGINES INSTALLED. NO CREDIT CARD NEEDED.")

if __name__ == "__main__":
    main()
