import os
import json
import random
import logging
import google.generativeai as genai
from scripts.utils import file_tools

def select_topic():
    # Rotating topics to ensure variety
    topics = ["Lion", "Eagle", "Shark", "Wolf", "Tiger", "Bear", "Crocodile", "Elephant"]
    return random.choice(topics)

def generate_full_script(topic):
    logging.info(f"Generating AI Script for: {topic}")
    
    # Try Gemini First (Free & Fast)
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            You are a professional YouTube scriptwriter. Create a viral script about "{topic}".
            Structure:
            1. Title: Catchy and SEO optimized.
            2. Description: For YouTube video description with hashtags.
            3. Segments: Exactly 10 segments. Each segment must have:
               - "text": 2 sentences of narration (engaging facts).
               - "keywords": 1 specific visual search term for stock video (e.g., "{topic} hunting", "{topic} eyes").
            
            Output strictly valid JSON:
            {{
                "topic": "{topic}",
                "title": "...",
                "description": "...",
                "hashtags": ["#tag1", "#tag2"],
                "segments": [
                    {{"text": "...", "keywords": ["..."]}},
                    ...
                ]
            }}
            """
            response = model.generate_content(prompt)
            # Clean up response to ensure valid JSON
            clean_json = response.text.replace("```json", "").replace("```", "")
            return json.loads(clean_json)
        except Exception as e:
            logging.error(f"Gemini Error: {e}")
    
    # Fallback if AI fails (Basic Template)
    return {
        "topic": topic,
        "title": f"10 Amazing Facts About {topic}",
        "description": f"Learn about {topic}...",
        "hashtags": ["#animals", f"#{topic}"],
        "segments": [
            {"text": f"The {topic} is one of the most fascinating animals.", "keywords": [topic]},
            {"text": "They are known for their incredible strength.", "keywords": [f"{topic} running"]},
            {"text": "Few people know this secret fact about them.", "keywords": [f"{topic} face"]},
            {"text": "They can survive in extreme conditions.", "keywords": [f"{topic} nature"]},
            {"text": "Subscribe for more amazing animal facts.", "keywords": ["subscribe animation"]}
        ]
    }