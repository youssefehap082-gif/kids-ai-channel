# المسار: src/ai_content.py

import requests
import json
import time
from src.config import HF_API_TOKEN, HF_LLM_MODEL

HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_LLM_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def query_hf_inference(payload, retries=3, delay=10):
    """
    Helper function to query HF Inference API with retries for cold start.
    """
    for attempt in range(retries):
        try:
            response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            
            output = response.json()
            if isinstance(output, list):
                output = output[0]
            
            # The model generates text inside 'generated_text'
            generated_text = output.get('generated_text', '')
            
            # Mistral includes the prompt in the response, we need to strip it.
            if ']' in generated_text:
                 generated_text = generated_text.split(']')[-1].strip()

            # The model might return text *before* the JSON. We find the JSON.
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = generated_text[json_start:json_end]
                # Clean up potential markdown
                json_str = json_str.replace("```json\n", "").replace("\n```", "")
                return json.loads(json_str)
            else:
                raise ValueError(f"No valid JSON found in HF response: {generated_text}")
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503 and attempt < retries - 1:
                print(f"Model is loading (503)... retrying in {delay}s. (Attempt {attempt+1})")
                time.sleep(delay)
            else:
                raise e
        except Exception as e:
            print(f"Error during HF query: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e
    raise Exception("Failed to get response from Hugging Face after retries.")


def get_animal_ideas(used_animals: list, count: int = 6) -> list:
    """
    يجيب 6 أفكار حيوانات جديدة (2 للـ Long، 4 للـ Shorts)
    """
    print(f"Getting {count} new animal ideas, avoiding: {used_animals}")
    
    prompt = f"""
    [INST]
    You are an expert viral YouTube producer.
    Give me a list of {count} animals for YouTube videos.
    The audience is international (English-speaking).
    DO NOT include any of the following animals: {', '.join(used_animals)}
    
    Respond ONLY with a JSON list of strings.
    Example: {{"animals": ["Red Panda", "Axolotl", "Capybara", "Fennec Fox", "Honey Badger", "Platypus"]}}
    [/INST]
    """
    
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250}}
    data = query_hf_inference(payload)
    animals = data.get("animals", [])
    print(f"Generated ideas: {animals}")
    return animals

def generate_long_video_script(animal_name: str) -> dict:
    """
    ينشئ سكريبت كامل لفيديو طويل (10 حقائق) + SEO
    """
    print(f"Generating long video script for: {animal_name}")
    prompt = f"""
    [INST]
    Create a complete content package for a YouTube video about the "{animal_name}".
    The script must contain exactly 10 interesting, verifiable facts.

    Format the output as a single JSON object with these keys:
    1. "title": A catchy, SEO-optimized YouTube title (under 70 chars).
    2. "description": A 300-word YouTube description with keywords.
    3. "tags": A list of 15 relevant YouTube tags/keywords.
    4. "facts": A list of 10 strings (each is a single fact for the voiceover).
    
    Respond ONLY with the JSON object.
    [/INST]
    """
    
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 1500}}
    content_package = query_hf_inference(payload)
    return content_package

def generate_short_video_idea(animal_name: str) -> dict:
    """
    ينشئ SEO لفيديو قصير (موسيقى فقط)
    """
    print(f"Generating short video metadata for: {animal_name}")
    prompt = f"""
    [INST]
    Create a content package for a YouTube SHORT about the "{animal_name}".
    The video will be music-only, showing beautiful clips.

    Format the output as a single JSON object with these keys:
    1. "title": A viral, catchy, SEO-optimized YouTube Short title (e.g., "The Majestic {animal_name} 🤯 #shorts").
    2. "description": A short 100-word description with hashtags.
    3. "tags": A list of 10 relevant YouTube tags/keywords (include #shorts).
    
    Respond ONLY with the JSON object.
    [/INST]
    """
    
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 500}}
    content_package = query_hf_inference(payload)
    return content_package
