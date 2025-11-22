import os
import json

# ==========================================
# PHASE 7: THE BEAST UPDATE (WIKIPEDIA + EDGE TTS + MEGA LIST)
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

    # 1. MEGA ANIMALS LIST (Huge Variety)
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

    # 2. CONTENT ENGINE (Wikipedia + Viral Hooks)
    content_engine = """
import random
import wikipedia

def get_wiki_summary(animal):
    print(f"📚 Searching Wikipedia for: {animal}")
    try:
        # Get summary from Wikipedia
        wikipedia.set_lang("en")
        # Try to get a summary, handle ambiguity
        try:
            summary = wikipedia.summary(animal, sentences=5)
        except wikipedia.exceptions.DisambiguationError as e:
            summary = wikipedia.summary(e.options[0], sentences=5)
        return summary
    except Exception as e:
        print(f"⚠️ Wikipedia Error: {e}")
        return f"The {animal} is one of the most fascinating creatures on Earth. Scientists are constantly discovering new facts about its behavior and habitat."

def generate_script(animal_name, mode="short"):
    print(f"📝 Writing Script ({mode}) for: {animal_name}")
    
    # 1. Fetch Real Info
    wiki_text = get_wiki_summary(animal_name)
    
    # Clean up text (remove brackets like [1])
    import re
    wiki_text = re.sub(r'\[.*?\]', '', wiki_text)
    
    # 2. Viral Hooks
    hooks = [
        f"You won't believe what the {animal_name} can do!",
        f"The {animal_name} is nature's ultimate machine.",
        f"Stop scrolling! Learn the truth about the {animal_name}.",
        f"Why is the {animal_name} so dangerous?",
        f"This is the most amazing fact about the {animal_name}."
    ]
    hook = random.choice(hooks)
    
    if mode == "long":
        # DOCUMENTARY STYLE
        sentences = wiki_text.split('. ')
        body = ". ".join(sentences[:6]) # Take first 6 sentences
        
        script_text = f"{hook} Welcome to a deep dive into the world of the {animal_name}. {body}. These creatures are truly a marvel of evolution. Their survival instincts are unmatched in the wild. Thank you for watching this documentary. Like and subscribe for more wildlife secrets."
        
        title = f"The Life of {animal_name}: Full Documentary 🌍"
        desc = f"Watch this full documentary about the {animal_name}. Real facts, amazing footage.\\n\\n#animals #wildlife #documentary #{animal_name.replace(' ', '')} #nature"
        tags = ["animals", "wildlife", "documentary", "nature", animal_name, "science", "education"]
        
    else:
        # SHORTS STYLE
        sentences = wiki_text.split('. ')
        fact1 = sentences[0] if len(sentences) > 0 else "It is amazing."
        fact2 = sentences[1] if len(sentences) > 1 else "It lives in the wild."
        
        script_text = f"{hook} Did you know? {fact1}. Also, {fact2}. Subscribe for more wild facts!"
        
        title = f"{animal_name}: The Shocking Truth 🤯 #shorts"
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

    # 3. VOICE ENGINE (EDGE TTS - THE GAME CHANGER)
    voice_engine = """
import asyncio
import edge_tts
import os

async def _generate_voice_async(text, output_path):
    # Voice: Male, Deep, Documentary Style (Christopher)
    voice = "en-US-ChristopherNeural"
    # Speed: +10% for better retention
    rate = "+10%"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate)
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

    # 4. EDITOR ENGINE (FIXED MUSIC & ASPECT RATIO)
    editor_engine = """
import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, vfx

def create_video(video_paths, audio_path, music_path=None, mode="short", output_path="assets/final_video.mp4"):
    print(f"🎬 Editing Video (Mode: {mode})...")
    
    try:
        voice_audio = AudioFileClip(audio_path)
        target_duration = voice_audio.duration + 1.0
        
        clips = []
        current_duration = 0
        
        # Resolution Targets
        # Short: 1080x1920 (9:16)
        # Long:  1920x1080 (16:9)
        
        while current_duration < target_duration:
            for path in video_paths:
                try:
                    clip = VideoFileClip(path)
                    
                    if mode == "short":
                         # Force Portrait
                         if clip.h != 1920: clip = clip.resize(height=1920)
                         if clip.w > 1080:
                            clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
                    else:
                         # Force Landscape
                         if clip.w != 1920: clip = clip.resize(width=1920)
                         if clip.h > 1080:
                            clip = clip.crop(x1=0, y1=clip.h/2 - 540, width=1920, height=1080)
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
        
        # --- AUDIO MIXING ---
        final_audio = voice_audio
        
        if music_path and os.path.exists(music_path):
            print("🎵 Mixing Background Music...")
            try:
                music = AudioFileClip(music_path)
                # Loop to fit video
                if music.duration < target_duration:
                    music = music.loop(duration=target_duration)
                else:
                    music = music.subclip(0, target_duration)
                
                # Reduce Music Volume to 15%
                music = music.volumex(0.15)
                
                # Combine
                final_audio = CompositeAudioClip([voice_audio, music])
            except Exception as e:
                print(f"⚠️ Audio Mix Failed: {e}")

        final_clip = final_clip.set_audio(final_audio)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # High Bitrate
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
        img = img.point(lambda p: p * 0.6) # Darken
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        draw.text((50, 50), text, font=font, fill=(255, 255, 0))
        img.save(output_path)
        return output_path
    except: return None
"""
    create_file("scripts/editor_engine.py", editor_engine)

    # 5. MAIN PIPELINE (FORCED DOUBLE RUN)
    main_pipeline = """
import os
import sys
import json
import random

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
        return "Lion"

def execute_run(mode):
    print(f"\\n🚀 EXECUTING PIPELINE: {mode.upper()} MODE")
    
    # 1. Pick Animal
    animal = get_random_animal()
    print(f"🦁 Subject: {animal}")
    
    # 2. Script (Wikipedia)
    script_data = generate_script(animal, mode=mode)
    
    # 3. Voice (Edge TTS)
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: return

    # 4. Music Check
    local_music = "background.mp3"
    music_path = local_music if os.path.exists(local_music) else None
    if not music_path: print("⚠️ WARNING: background.mp3 not found!")

    # 5. Media
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

    # 6. Edit
    final_video = create_video(local_videos, audio_path, music_path, mode=mode)
    if not final_video: return

    # 7. Thumbnail (For Long)
    thumb_path = None
    if mode == "long":
        raw_thumb = get_thumbnail_image(animal)
        if raw_thumb:
            thumb_path = create_thumbnail(raw_thumb, f"{animal} FACTS")

    # 8. Upload
    video_id = upload_video(
        final_video, 
        script_data['title'], 
        script_data['description'], 
        script_data['tags'],
        thumb_path
    )
    
    if video_id:
        print(f"✅ SUCCESS! {mode} video live: https://youtu.be/{video_id}")

if __name__ == "__main__":
    # This enforces 1 Short AND 1 Long run immediately
    print("🧪 TEST MODE: Generating 1 Short & 1 Long Video...")
    
    execute_run("short")
    print("\\n--- Short Done. Starting Long... ---\\n")
    execute_run("long")
"""
    create_file("scripts/main_pipeline.py", main_pipeline)

    # 6. WORKFLOW (Add wikipedia & edge-tts)
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
        run: pip install openai requests google-api
