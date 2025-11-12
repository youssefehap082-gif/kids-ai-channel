# المسار: src/audio_generation.py

import os
import requests
import time
from src.config import (
    ASSETS_DIR, PEXELS_API_KEY, PIXABAY_API_KEY, 
    HF_API_TOKEN, HF_TTS_MODEL
)

TTS_API_URL = f"https://api-inference.huggingface.co/models/{HF_TTS_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def create_voiceover(text: str, filepath: str, retries=3, delay=10):
    """
    ينشئ ملف صوتي واحد (بصوت مجاني واحد)
    """
    print(f"Generating VO (Free) for: {text[:20]}...")
    payload = {"inputs": text}
    
    for attempt in range(retries):
        try:
            response = requests.post(TTS_API_URL, headers=HEADERS, json=payload)
            response.raise_for_status() # Check for HTTP errors
            
            # The response is raw audio data
            if response.content:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"Saved VO to {filepath}")
                return
            else:
                raise Exception("Empty audio response")
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503 and attempt < retries - 1:
                print(f"TTS Model is loading (503)... retrying in {delay}s. (Attempt {attempt+1})")
                time.sleep(delay)
            else:
                print(f"Error generating VO: {e}")
                raise e
        except Exception as e:
            print(f"Error saving VO file: {e}")
            raise e
            
    raise Exception("Failed to generate VO after retries.")


def generate_all_vo_files(facts: list) -> (list, list):
    """
    ينشئ ملفات صوتية لكل حقيقة + ملف الـ CTA (بنفس الصوت)
    """
    os.makedirs(ASSETS_DIR, exist_ok=True)
    vo_files = []
    vo_durations = []
    
    from moviepy.editor import AudioFileClip

    # 1. إنشاء ملفات الحقائق
    for i, fact in enumerate(facts):
        # HF TTS بيكره النصوص الطويلة، ممكن نقسمها لو احتجنا
        # (بس هنا بنفترض إن الجملة الواحدة مناسبة)
        filepath = os.path.join(ASSETS_DIR, f"fact_{i}.mp3")
        create_voiceover(fact, filepath)
        vo_files.append(filepath)
        with AudioFileClip(filepath) as clip:
            vo_durations.append(clip.duration)
        time.sleep(2) # عشان ندي الـ API فرصة (مجاني بقى)

    # 2. إنشاء ملف الـ CTA
    cta_text = "Don’t forget to subscribe and hit the bell for more!"
    cta_filepath = os.path.join(ASSETS_DIR, "cta.mp3")
    create_voiceover(cta_text, cta_filepath)
    vo_files.append(cta_filepath)
    with AudioFileClip(cta_filepath) as clip:
        vo_durations.append(clip.duration)

    return vo_files, vo_durations

def get_copyright_free_music() -> str:
    """
    (ده زي ما هو - مكتبات الستوك مجانية أصلا)
    """
    print("Searching for copyright-free background music...")
    filepath = os.path.join(ASSETS_DIR, "background_music.mp3")
    
    try:
        # محاولة مع Pixabay
        params = {
            "key": PIXABAY_API_KEY,
            "q": "ambient documentary instrumental",
            "music": "true",
            "per_page": 5
        }
        response = requests.get("https://pixabay.com/api/music/", params=params)
        response.raise_for_status()
        tracks = response.json().get("hits", [])
        
        if tracks:
            track_url = tracks[0]["download_url"]
            print(f"Downloading music from Pixabay: {track_url}")
            headers_dl = {'User-Agent': 'Mozilla/5.0'}
            music_data = requests.get(track_url, headers=headers_dl)
            
            with open(filepath, "wb") as f:
                f.write(music_data.content)
            return filepath
        
    except Exception as e:
        print(f"Warning: Could not download music automatically: {e}")
        
    return None
