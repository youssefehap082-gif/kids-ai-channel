# المسار: src/ai_content.py

from openai import OpenAI
from src.config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def get_animal_ideas(used_animals: list, count: int = 7) -> list:
    """
    يجيب أفكار حيوانات جديدة (2 للـ Long، 5 للـ Shorts)
    """
    print(f"Getting {count} new animal ideas, avoiding: {used_animals}")
    system_prompt = f"""
    You are an expert viral YouTube producer.
    Give me a list of {count} animals for YouTube videos.
    The audience is international (English-speaking).
    DO NOT include any of the following animals: {', '.join(used_animals)}
    Only return a JSON list of strings. Example: ["Red Panda", "Axolotl"]
    """
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system_prompt}]
    )
    
    animals = json.loads(response.choices[0].message.content)
    print(f"Generated ideas: {animals}")
    return animals

def generate_long_video_script(animal_name: str) -> dict:
    """
    ينشئ سكريبت كامل لفيديو طويل (10 حقائق) + SEO
    """
    print(f"Generating long video script for: {animal_name}")
    prompt = f"""
    Create a complete content package for a YouTube video about the "{animal_name}".
    The target audience is international and loves nature documentaries.
    The script must contain exactly 10 interesting, verifiable facts.

    Format the output as a single JSON object with these keys:
    1. "title": A catchy, SEO-optimized YouTube title (under 70 chars).
    2. "description": A 300-word YouTube description. Start with a hook, include keywords like "wildlife", "documentary", "{animal_name} facts", and end with a call to subscribe.
    3. "tags": A list of 15 relevant YouTube tags/keywords.
    4. "facts": A list of 10 strings. Each string is a single fact for the voiceover.
    5. "short_title": A catchy title for a YouTube Short (under 40 chars).
    
    Example for "facts":
    ["Fact 1: The Fennec Fox has the largest ears relative to its body size...", "Fact 2: These giant ears are used to dissipate heat..."]
    """
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt}]
    )
    
    content_package = json.loads(response.choices[0].message.content)
    return content_package

def generate_short_video_idea(animal_name: str) -> dict:
    """
    ينشئ SEO لفيديو قصير (موسيقى فقط)
    """
    print(f"Generating short video metadata for: {animal_name}")
    prompt = f"""
    Create a content package for a YouTube SHORT about the "{animal_name}".
    The video will be music-only, showing beautiful clips.

    Format the output as a single JSON object with these keys:
    1. "title": A viral, catchy, SEO-optimized YouTube Short title (e.g., "The Majestic {animal_name} in 60 seconds 🤯 #shorts").
    2. "description": A short 100-word description with hashtags.
    3. "tags": A list of 10 relevant YouTube tags/keywords (include #shorts).
    """
    
    response = client.chat.completions.create(
        model="gpt-4o", # أسرع وأرخص للشورتات
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt}]
    )
    
    content_package = json.loads(response.choices[0].message.content)
    return content_package

def translate_srt(srt_content: str, language_code: str, language_name: str) -> str:
    """
    يستخدم GPT لترجمة ملفات الترجمة (SRT)
    """
    print(f"Translating SRT to {language_name} ({language_code})")
    system_prompt = f"""
    You are an expert translator specializing in YouTube subtitles.
    Translate the following English SRT content into {language_name}.
    
    RULES:
    1. DO NOT change the timestamps (e.g., "00:00:01,000 --> 00:00:05,000").
    2. DO NOT change the sequence numbers (e.g., "1", "2", "3").
    3. Only translate the subtitle text itself.
    4. Return ONLY the translated SRT content.
    
    Original SRT:
    {srt_content}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o", # ممتاز في الترجمة
        messages=[{"role": "system", "content": system_prompt}]
    )
    
    return response.choices[0].message.content
