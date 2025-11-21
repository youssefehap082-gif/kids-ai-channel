import os
import json

# ==========================================
# PHASE 6: VIRAL UPDATE (SEO, MUSIC FIX, MEGA LIST)
# ==========================================

PROJECT_NAME = "." 

def create_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Updated: {path}")

def main():
    print("🚀 INSTALLING PHASE 6 (VIRAL ENGINES)...")

    # 1. MEGA ANIMALS LIST (No More Duplicates)
    animals_data = {
        "categories": {
            "Predators": ["Lion", "Tiger", "Jaguar", "Polar Bear", "Komodo Dragon", "Great White Shark", "Crocodile", "Leopard", "Wolf", "Hyena"],
            "Cute": ["Red Panda", "Quokka", "Sea Otter", "Capybara", "Fennec Fox", "Koala", "Sloth", "Meerkat", "Hedgehog", "Penguin"],
            "Ocean": ["Octopus", "Blue Whale", "Mantis Shrimp", "Seahorse", "Jellyfish", "Narwhal", "Giant Squid", "Orca", "Hammerhead Shark"],
            "Birds": ["Shoebill Stork", "Peregrine Falcon", "Owl", "Parrot", "Flamingo", "Peacock", "Eagle", "Hummingbird", "Toucan"],
            "Insects": ["Praying Mantis", "Hercules Beetle", "Butterfly", "Tarantula", "Scorpion", "Honey Bee", "Ant Colony"],
            "Weird": ["Platypus", "Blobfish", "Axolotl", "Pangolin", "Tapir", "Aye-Aye", "Star-nosed Mole"]
        }
    }
    create_file("config/animals_list.json", json.dumps(animals_data, indent=4))

    # 2. CONTENT ENGINE (Viral SEO + Templates)
    content_engine = """
import random

def generate_script(animal_name, mode="short"):
    print(f"📝 Writing Viral Script ({mode}) for: {animal_name}")
    
    # Viral Hooks
    hooks = [
        f"You won't believe this about the {animal_name}!",
        f"This is why the {animal_name} is the craziest animal on earth.",
        f"Stop scrolling! Look at this {animal_name}.",
        f"The shocking truth about the {animal_name}.",
        f"Never get close to a {animal_name}, here is why."
    ]
    
    # Facts Template (Generic to ensure it works for all)
    facts = [
        f"The {animal_name} has abilities that scientists can't fully explain.",
        f"They are known to survive in extreme conditions.",
        f"Their hunting strategy is absolutely unique in the animal kingdom.",
        f"A baby {animal_name} is one of the cutest things you will ever see.",
        f"They can move faster than you think.",
        f"Their population is rare and they are hard to find in the wild.",
        f"They have a very special way of communicating with each other."
    ]
    random.shuffle(facts)
    
    hook = random.choice(hooks)
    
    if mode == "long":
        # Long Form Structure
        script_text = f"{hook} Welcome to the world of the {animal_name}. {facts[0]}. {facts[1]}. {facts[2]}. {facts[3]}. {facts[4]}. Truly an amazing creature. Thanks for watching!"
        title = f"10 Shocking Facts About {animal_name} 🌍 (Documentary)"
        desc = f"Discover the secrets of the {animal_name}. Amazing wildlife documentary.\\n\\n#animals #wildlife #{animal_name.replace(' ', '')} #nature #documentary"
        tags = ["animals", "wildlife", "documentary", "nature", animal_name, "facts"]
    else:
        # Shorts Structure
        script_text = f"{hook} Did you know? {facts[0]}. {facts[1]}. {facts[2]}. Subscribe for more!"
        title = f"{animal_name} Facts that will Blow Your Mind 🤯 #shorts"
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

    # 3. VOICE ENGINE (Faster Speed = More Excitement)
    voice_engine = """
from gtts import gTTS
import os

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voice (US Accent)...")
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # US Accent for better engagement
        tts = gTTS(text=text, lang='en', tld='us', slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None
"""
    create_file("scripts/voice_engine.py", voice_engine)

    # 4. EDITOR ENGINE (Music Fix + Speed Boost)
    editor_engine = """
import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, vfx

def create_video(video_paths, audio_path, music_path=None, mode="short", output_path="assets/final_video.mp4"):
    print(f"🎬 Editing Video (Mode: {mode})...")
    
    try:
        # 1. Load Voice & Speed it up (1.1x for excitement)
        voice_audio = AudioFileClip(audio_path)
        voice_audio = voice_audio.fx(vfx.speedx, 1.1) # تسرع الصوت قليلاً
        
        target_duration = voice_audio.duration + 1.5
        
        # 2. Prepare Video Clips
        clips = []
        current_duration = 0
        
        while current_duration < target_duration:
            for path in video_paths:
                try:
                    clip = VideoFileClip(path)
                    
                    # Resize Logic
                    if mode == "short":
                         if clip.h != 1920: clip = clip.resize(height=1920)
                         clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
                    else:
                         # Long Mode (Landscape)
                         if clip.w != 1920: clip = clip.resize(width=1920)
                         clip = clip.crop(x1=0, y1=clip.h/2 - 540, width=1920, height=1080)

                    clips.append(clip)
                    current_duration += clip.duration
                    if current_duration >= target_duration: break
                except: continue
        
        if not clips: return None

        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.subclip(0, target_duration)
        
        # 3. Add Background Music (Strict Fix)
        final_audio = voice_audio
        
        if music_path and os.path.exists(music_path):
            print(f"🎵 Adding Music from: {music_path}")
            try:
                music = AudioFileClip(music_path)
                # Loop music if shorter
                if music.duration < target_duration:
                    music = music.loop(duration=target_duration)
                else:
                    music = music.subclip(0, target_duration)
                
                # Lower volume to 10%
                music = music.volumex(0.10)
                
                # Mix
                final_audio = CompositeAudioClip([voice_audio, music])
                print("✅ Music Mixed Successfully.")
            except Exception as e:
                print(f"⚠️ Music Mix Failed: {e}")
        else:
            print("⚠️ WARNING: No Music File Found! Video will be voice only.")

        final_clip = final_clip.set_audio(final_audio)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=2, preset='ultrafast')
        
        return output_path
        
    except Exception as e:
        print(f"❌ Editing Error: {e}")
        return None

# Thumbnail Logic (Simple Text)
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

    # 5. MAIN PIPELINE (Double Run: Short THEN Long)
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
        return "Lion"

def execute_run(mode_override=None):
    print(f"🚀 Starting Pipeline Run... Mode: {mode_override}")
    
    # Logic to determine mode
    if mode_override:
        mode = mode_override
    else:
        # Automatic Schedule Logic
        current_hour = datetime.datetime.utcnow().hour
        if current_hour == 12: # 12 PM UTC = Long Video
            mode = "long"
        else:
            mode = "short"
    
    orientation = "landscape" if mode == "long" else "portrait"
    animal = get_random_animal()
    
    print(f"🦁 Animal: {animal} | Mode: {mode}")
    
    script_data = generate_script(animal, mode=mode)
    audio_path = generate_voice(script_data['script_text'])
    if not audio_path: return

    # Music Check
    local_music = "background.mp3"
    music_path = local_music if os.path.exists(local_music) else None
    if not music_path: print("⚠️ NOTE: background.mp3 not found in root folder!")

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
        print(f"🎉 SUCCESS! {mode.upper()} Video Live: https://youtu.be/{video_id}")

if __name__ == "__main__":
    # TEST RUN: Run BOTH modes immediately
    print("🧪 TEST RUN INITIATED: 1 Short + 1 Long")
    
    print("--- STEP 1: MAKING SHORT ---")
    execute_run(mode_override="short")
    
    print("\\n--- STEP 2: MAKING LONG ---")
    execute_run(mode_override="long")
    
    print("\\n🏁 TEST RUN COMPLETE.")
"""
    create_file("scripts/main_pipeline.py", main_pipeline)

    print("\n👑 PHASE 6 INSTALLED. READY FOR DOUBLE TEST.")

if __name__ == "__main__":
    main()
