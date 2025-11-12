# المسار: src/video_assembly.py

import os
import requests
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    TextClip, concatenate_videoclips, vfx
)
from moviepy.audio.fx.all import audio_loop, volumex
from src.config import PEXELS_API_KEY, ASSETS_DIR

# --- Helpers ---

def get_stock_videos(query: str, count: int) -> list:
    """
    يجيب فيديوهات ستوك من Pexels
    """
    print(f"Searching Pexels for: {query} (need {count} clips)")
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": count, "orientation": "landscape"}
    
    try:
        response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
        response.raise_for_status()
        videos = response.json().get("videos", [])
        
        video_files = []
        for video in videos:
            # بنختار جودة HD عشان GitHub runner يقدر يتعامل معاها
            link = next((f['link'] for f in video['video_files'] if f['quality'] == 'hd'), None)
            if not link:
                link = video['video_files'][0]['link'] # أي جودة وخلاص
            
            print(f"Downloading clip: {video['id']}")
            clip_data = requests.get(link, headers=headers)
            filepath = os.path.join(ASSETS_DIR, f"stock_{video['id']}.mp4")
            with open(filepath, "wb") as f:
                f.write(clip_data.content)
            video_files.append(filepath)
        
        if not video_files:
            raise Exception("No video clips found on Pexels")
        
        return video_files
        
    except Exception as e:
        print(f"Error fetching Pexels videos: {e}")
        return []

def create_text_clip(text: str, duration: float) -> TextClip:
    """
    ينشئ مقطع نصي (للحقائق والـ CTA)
    """
    return TextClip(
        text,
        fontsize=70,
        color='white',
        font='Arial-Bold',
        stroke_color='black',
        stroke_width=2,
        size=(1920, 1080), # 1080p
        method='caption',
        align='center',
        bg_color='transparent'
    ).set_duration(duration).set_position(('center', 0.8)) # في التلت اللي تحت

# --- Main Functions ---

def assemble_long_video(animal: str, facts: list, vo_files: list, vo_durations: list, music_file: str) -> str:
    """
    تجميع الفيديو الطويل (10 حقائق)
    """
    print(f"Starting long video assembly for: {animal}")
    
    # 1. جلب الفيديوهات (محتاجين 11 مقطع: 10 للحقائق + 1 للـ CTA)
    stock_clips = get_stock_videos(animal, 11)
    if len(stock_clips) < 11:
        print("Warning: Not enough stock clips. Re-using clips.")
        stock_clips = (stock_clips * (11 // len(stock_clips) + 1))[:11]

    final_clips = []
    
    # 2. تجميع مقاطع الحقائق
    for i, fact in enumerate(facts):
        duration = vo_durations[i]
        vo_clip = AudioFileClip(vo_files[i])
        video_clip = VideoFileClip(stock_clips[i]).subclip(0, duration)
        
        # إضافة نص الحقيقة (مثال: "Fact #1")
        fact_title = create_text_clip(f"Fact #{i+1}", duration)
        
        composite = CompositeVideoClip([video_clip, fact_title])
        composite = composite.set_audio(vo_clip)
        final_clips.append(composite)

    # 3. تجميع مقطع الـ CTA
    cta_duration = vo_durations[-1]
    cta_vo = AudioFileClip(vo_files[-1])
    cta_video = VideoFileClip(stock_clips[-1]).subclip(0, cta_duration)
    cta_text = create_text_clip("Don’t forget to subscribe!", cta_duration)
    
    cta_composite = CompositeVideoClip([cta_video, cta_text])
    cta_composite = cta_composite.set_audio(cta_vo)
    final_clips.append(cta_composite)
    
    # 4. تجميع الفيديو النهائي
    video = concatenate_videoclips(final_clips)
    
    # 5. إضافة الموسيقى
    if music_file:
        music = (AudioFileClip(music_file)
                 .fx(audio_loop, duration=video.duration)
                 .fx(volumex, 0.1)) # بنوطي صوت الموسيقى جداً
        
        # دمج صوت التعليق مع الموسيقى
        final_audio = CompositeAudioClip([video.audio, music])
        video = video.set_audio(final_audio)

    # 6. تصدير الملف
    output_path = os.path.join(ASSETS_DIR, f"{animal}_long_video.mp4")
    video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        threads=4, # عشان السرعة على الـ Runner
        fps=24
    )
    print(f"Long video finished: {output_path}")
    return output_path

def assemble_short_video(animal: str, music_file: str) -> str:
    """
    تجميع فيديو قصير (موسيقى فقط)
    """
    print(f"Starting short video assembly for: {animal}")
    
    # 1. جلب الفيديوهات (3 مقاطع قصيرة)
    stock_clips = get_stock_videos(animal, 3)
    if not stock_clips:
        raise Exception("No clips for short")
    
    # 2. قص وتجهيز الفيديوهات
    clips_processed = []
    total_duration = 0
    target_duration = 55 # أقل من 60 ثانية
    
    for clip_path in stock_clips:
        clip = VideoFileClip(clip_path)
        # تحويله لـ 9:16 (بورتريه)
        (w, h) = clip.size
        target_w = h * 9 / 16
        clip_cropped = clip.fx(vfx.crop, x_center=w/2, width=target_w)
        clip_resized = clip_cropped.resize(height=1920) # 1080x1920
        
        # قص 18 ثانية من كل مقطع
        duration = min(clip.duration, 18.0)
        clips_processed.append(clip_resized.subclip(0, duration))
        total_duration += duration
        if total_duration >= target_duration:
            break
            
    # 3. تجميع الفيديو
    video = concatenate_videoclips(clips_processed).subclip(0, target_duration)
    
    # 4. إضافة الموسيقى
    if music_file:
        music = (AudioFileClip(music_file)
                 .fx(audio_loop, duration=video.duration)
                 .fx(volumex, 0.8)) # الموسيقى هنا عالية
        video = video.set_audio(music)
    
    # 5. إضافة الـ CTA (كنص فقط)
    cta_text = create_text_clip("Subscribe for more!", 5).set_start(target_duration - 6)
    video = CompositeVideoClip([video, cta_text])
    
    # 6. تصدير الملف
    output_path = os.path.join(ASSETS_DIR, f"{animal}_short_video.mp4")
    video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        threads=4,
        fps=24
    )
    print(f"Short video finished: {output_path}")
    return output_path
