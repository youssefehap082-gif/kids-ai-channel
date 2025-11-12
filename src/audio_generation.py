# المسار: src/audio_generation.py

import os
import requests
from elevenlabs import save
from elevenlabs.client import ElevenLabs
from src.config import (
    ELEVEN_API_KEY, VOICE_ID_MALE, VOICE_ID_FEMALE, 
    ASSETS_DIR, PEXELS_API_KEY, PIXABAY_API_KEY
)

client = ElevenLabs(api_key=ELEVEN_API_KEY)

def create_voiceover(text: str, filepath: str, gender: str = "male"):
    """
    ينشئ ملف صوتي واحد
    """
    print(f"Generating VO ({gender}) for: {text[:20]}...")
    voice_id = VOICE_ID_MALE if gender == "male" else VOICE_ID_FEMALE
    
    audio = client.generate(
        text=text,
        voice=voice_id,
        model="eleven_multilingual_v2" # بيدعم الإنجليزي بطلاقة
    )
    
    save(audio, filepath)
    print(f"Saved VO to {filepath}")

def generate_all_vo_files(facts: list, gender: str) -> (list, list):
    """
    ينشئ ملفات صوتية لكل حقيقة + ملف الـ CTA
    """
    os.makedirs(ASSETS_DIR, exist_ok=True)
    vo_files = []
    vo_durations = []
    
    from moviepy.editor import AudioFileClip

    # 1. إنشاء ملفات الحقائق
    for i, fact in enumerate(facts):
        filepath = os.path.join(ASSETS_DIR, f"fact_{i}.mp3")
        create_voiceover(fact, filepath, gender)
        vo_files.append(filepath)
        # بنحسب مدة الملف عشان نظبط الفيديو عليه
        with AudioFileClip(filepath) as clip:
            vo_durations.append(clip.duration)

    # 2. إنشاء ملف الـ CTA
    cta_text = "Don’t forget to subscribe and hit the bell for more!"
    cta_filepath = os.path.join(ASSETS_DIR, "cta.mp3")
    create_voiceover(cta_text, cta_filepath, gender)
    vo_files.append(cta_filepath)
    with AudioFileClip(cta_filepath) as clip:
        vo_durations.append(clip.duration)

    return vo_files, vo_durations

def get_copyright_free_music() -> str:
    """
    يحاول يجيب موسيقى (بدون حقوق) من Pexels أو Pixabay
    """
    print("Searching for copyright-free background music...")
    filepath = os.path.join(ASSETS_DIR, "background_music.mp3")
    
    try:
        # محاولة مع Pexels
        headers = {"Authorization": PEXELS_API_KEY}
        # Pexels مفيهاش بحث صوتي سهل، فممكن نستخدم Pixabay
        
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
            
            # Pixabay بتحتاج user-agent
            headers_dl = {'User-Agent': 'Mozilla/5.0'}
            music_data = requests.get(track_url, headers=headers_dl)
            
            with open(filepath, "wb") as f:
                f.write(music_data.content)
            return filepath
        
    except Exception as e:
        print(f"Warning: Could not download music automatically: {e}")
        # حل بديل: ممكن نحط ملف موسيقى يدوي في الـ repo
        
    return None # في حالة الفشل
