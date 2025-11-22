import os
import json

# ==========================================
# PHASE 7: WIKIPEDIA + EDGE TTS + PRO EDITING
# ==========================================

PROJECT_NAME = "." 

def create_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Updated: {path}")

def main():
    print("🚀 INSTALLING PHASE 7 (NATIONAL GEOGRAPHIC MODE)...")

    # 1. MEGA ANIMALS LIST (Categorized)
    animals_data = {
        "categories": {
            "Predators": ["Lion", "Tiger", "Jaguar", "Polar Bear", "Komodo Dragon", "Great White Shark", "Saltwater Crocodile", "Leopard", "Gray Wolf", "Spotted Hyena", "Cheetah", "Grizzly Bear"],
            "Cute": ["Red Panda", "Quokka", "Sea Otter", "Capybara", "Fennec Fox", "Koala", "Sloth", "Meerkat", "Hedgehog", "Emperor Penguin", "Giant Panda", "Raccoon"],
            "Ocean": ["Mimic Octopus", "Blue Whale", "Mantis Shrimp", "Seahorse", "Box Jellyfish", "Narwhal", "Giant Squid", "Orca", "Hammerhead Shark", "Manta Ray", "Pufferfish"],
            "Birds": ["Shoebill Stork", "Peregrine Falcon", "Snowy Owl", "Macaw", "Flamingo", "Peacock", "Bald Eagle", "Hummingbird", "Toucan", "Cassowary", "Albatross"],
            "Insects": ["Praying Mantis", "Hercules Beetle", "Monarch Butterfly", "Tarantula", "Emperor Scorpion", "Honey Bee", "Army Ant", "Dragonfly"],
            "Weird": ["Platypus", "Blobfish", "Axolotl", "Pangolin", "Malayan Tapir", "Aye-Aye", "Star-nosed Mole", "Okapi", "Proboscis Monkey"]
        }
    }
    create_file("config/animals_list.json", json.dumps(animals_data, indent=4))

    # 2. CONTENT ENGINE (Wikipedia + Hook)
    content_engine = """
import random
import wikipedia

def get_wiki_summary(animal):
    try:
        # Search and get summary
        wikipedia.set_lang("en")
        summary = wikipedia.summary(animal, sentences=4)
        return summary
    except:
        return f"The {animal} is a fascinating creature found in the wild. It has unique behaviors that scientists are still studying."

def generate_script(animal_name, mode="short"):
    print(f"📝 Researching & Writing ({mode}) for: {animal_name}")
    
    # 1. Get Real Facts from Wikipedia
    real_info = get_wiki_summary(animal_name)
    
    # 2. Viral Hooks
    hooks = [
        f"You won't believe what the {animal_name} can do!",
        f"The {animal_name} is nature's perfect machine.",
        f"This is why you should never mess with a {animal_name}.",
        f"The shocking truth about the {animal_name}.",
        f"Is the {animal_name} the smartest animal alive?"
    ]
    hook = random.choice(hooks)
    
    if mode == "long":
        # Long Form: Documentary Style
        script_text = f"{hook} {real_info} Let's dive deeper. {animal_name}s are known for their incredible survival skills. Unlike other species in their family, they have adapted perfectly to their environment. Watching them in the wild is a breathtaking experience. If you love nature, you have to respect the {animal_name}. Thanks for watching this documentary."
        title = f"The Life of {animal_name}: Full Documentary 🌍"
        desc = f"Watch this full documentary about the {animal_name}. Real facts, amazing footage.\\n\\n#animals #wildlife #documentary #{animal_name.replace(' ', '')} #nature"
        tags = ["animals", "wildlife", "documentary", "nature", animal_name, "science", "education"]
    else:
        # Shorts: Fast & Punchy
        script_text = f"{hook} Did you know? {real_info.split('.')[0]}. Also, {real_info.split('.')[1]}. Subscribe for more wild facts!"
        title = f"{animal_name}: The Truth Revealed 🤯 #shorts"
        desc = f"Crazy facts about {animal_name} #shorts #animals #wildlife"
        tags = ["shorts", "animals", "facts", "viral", animal_name]

    return {
        "title": title,
        "description": desc,
        "script_text": script_text,
        "tags": tags
    }
"""
    create_file("scripts/content_engine.py", content_engine)

    # 3. VOICE ENGINE (EDGE TTS - High Quality)
    voice_engine = """
import asyncio
import edge_tts
import os

async def _generate_voice_async(text, output_path):
    # voice: en-US-ChristopherNeural (Male) or en-US-AriaNeural (Female)
    # rate: +10% for excitement
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="+15%")
    await communicate.save(output_path)

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voice (Edge TTS - Pro Quality)...")
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        asyncio.run(_generate_voice_async(text, output_path))
        return output_path
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None
"""
    create_file("scripts/voice_engine.py", voice_engine)

    # 4. EDITOR ENGINE (Better Music Mixing)
    editor_engine = """
import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, vfx

def create_video(video_paths, audio_path, music_path=None, mode="short", output_path="assets/final_video.mp4"):
    print(f"🎬 Editing Video (Mode: {mode})...")
    
    try:
        voice_audio = AudioFileClip(audio_path)
        # Add padding at the end
        target_duration = voice_audio.duration + 1.0
        
        clips = []
        current_duration = 0
        
        # Target Resolutions
        # Long: 1920x1080 (Landscape) | Short: 1080x1920 (Portrait)
        
        while current_duration < target_duration:
            for path in video_paths:
                try:
                    clip = VideoFileClip(path)
                    
                    if mode == "short":
                         # Enforce 9:16
                         if clip.h != 1920: clip = clip.resize(height=1920)
                         if clip.w > 1080:
                            clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
                    else:
                         # Enforce 16:9 (Long)
                         # Resize based on width first to ensure it fills screen
                         if clip.w != 1920: clip = clip.resize(width=1920)
                         # If height is too tall, crop center
                         if clip.h > 1080:
                            clip = clip.crop(x1=0, y1=clip.h/2 - 540, width=1920, height=1080)
                         # If height is too short (rare for 1920 width), resize by height
                         elif clip.h < 1080:
                            clip = clip.resize(height=1080)
                            clip = clip.crop(x1=clip.w/2 - 960, y1=0, width=1920, height=1080)

                    clips.append(clip)
                    current_duration += clip.duration
                    if current_duration >= target_duration: break
                except: continue
        
        if not clips: return None

        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.subclip(0, target_duration)
        
        # --- PROFESSIONAL AUDIO MIXING ---
        final_audio = voice_audio
        
        if music_path and os.path.exists(music_path):
            print(f"🎵 Mixing Background Music...")
            try:
                music = AudioFileClip(music_path)
                
                # Loop music
                if music.duration < target_duration:
                    music = music.loop(duration=target_duration)
                else:
                    music = music.subclip(0, target_duration)
                
                # Volume Levels: Voice 100%, Music 15%
                music = music.volumex(0.15)
                
                final_audio = CompositeAudioClip([voice_audio, music])
            except Exception as e:
                print(f"⚠️ Audio Mix Warning: {e}")

        final_clip = final_clip.set_audio(final_audio)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Higher bitrate for quality
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=2, preset='ultrafast')
        
        return output_path
        
    except Exception as e:
        print(f"❌ Editing Error: {e}")
        return None

# Thumbnail Logic
from PIL import Image, ImageDraw, ImageFont
def create_thumbnail(image_path, text, output_path="assets/temp/final_thumb.jpg"):
    try:
        img = Image.open(image_path)
        # Make it pop: Increase contrast/saturation logic would go here, 
        # but for now we darken slightly for text readability
        img = img.point(lambda p: p * 0.7) 
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        except:
            font = ImageFont.load_default()
            
        # Draw Text (Yellow with Black Stroke if possible, simplified here)
        draw.text((60, 60), text, font=font, fill=(255, 255, 0)) # Yellow
        
        img.save(output_path)
        return output_path
    except: return None
"""
    create_file("scripts/editor_engine.py", editor_engine)

    # 5. MAIN PIPELINE (FORCE RUN: 1 SHORT + 1 LONG)
    main_pipeline = """
import os
import sys
import json
import random
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_engine import generate_script
from media_engine import gather_media, download_video, get_thumbnail_image
from voice_engine import generate_voice
from editor_engine import create_video, create_thumbnail
from uploader_engine import upload_video

def get_random_animal():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'animals_list.json')
        with open(config_path, 'r') as f:
            data = json.load(f)
        categories = list(data['categories'].keys())
        random_cat = random.choice(categories)
        return random.choice(data['categories'][random_cat])
    except:
        return "Tiger"

def execute_run(mode):
    print(f"\\n🎬 STARTING PIPELINE: {mode.upper()} MODE")
    
    animal = get_random_animal()
    print(f"🦁 Subject: {animal}")
    
    script_data = generate_script(animal, mode=mode)
    
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: return

    # Force Music
    local_music = "background.mp3"
    music_path = local_music if os.path.exists(local_music) else None
    if not music_path: print("⚠️ MISSING MUSIC: Please upload background.mp3")

    # Media
    orientation = "landscape" if mode == "long" else "portrait"
    video_urls = gather_media(animal, orientation=orientation)
    if not video_urls: return

    local_videos = []
    os.makedirs("assets/temp", exist_ok=True)
    for i, url in enumerate(video_urls):
        path = f"assets/temp/clip_{i}.mp4"
        try:
            download_video(url, path)
            local_videos.append(path)
        except: pass
    
    if not local_videos: return

    final_video = create_video(local_videos, audio_path, music_path, mode=mode)
    if not final_video: return

    # Thumbnail for Long Video
    thumb_path = None
    if mode == "long":
        raw_thumb = get_thumbnail_image(animal)
        if raw_thumb:
            thumb_path = create_thumbnail(raw_thumb, f"{animal} FACTS")

    video_id = upload_video(
        final_video, 
        script_data['title'], 
        script_data['description'], 
        script_data['tags'],
        thumb_path
    )
    
    if video_id:
        print(f"✅ SUCCESS! {mode} video: https://youtu.be/{video_id}")

if __name__ == "__main__":
    # This will run BOTH immediately for testing
    print("🧪 TEST MODE ACTIVATED: Generating 1 Short & 1 Long Video...")
    
    execute_run("short")
    execute_run("long")
    
    print("\\n🏁 ALL TASKS COMPLETED.")
"""
    create_file("scripts/main_pipeline.py", main_pipeline)

    # 6. GITHUB WORKFLOW (Install New Requirements)
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
        # Added edge-tts and wikipedia
        run: pip install openai requests google-api-python-client google-auth-oauthlib moviepy==1.0.3 imageio-ffmpeg gTTS edge-tts wikipedia

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

    print("\n👑 PHASE 7 INSTALLED. REAL FACTS, PRO VOICE, DOUBLE UPLOAD.")

if __name__ == "__main__":
    main()
