
import os
import json
import random
from openai import OpenAI

def generate_script(animal_name):
    print(f"📝 Generating Script for: {animal_name}")
    
    # Initialize Client (Standard OpenAI for now, easy to swap)
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f'''
    You are a YouTube scriptwriter for a viral animal channel.
    Topic: {animal_name}
    Style: Energetic, Mysterious, Fast-paced.
    Structure:
    1. Hook (0-5s): Shocking fact or question.
    2. Intro (5-15s): Quick intro.
    3. 5 Amazing Facts: Mix of scary/cute/bizarre.
    4. Conclusion: Call to action.
    
    Output format: JSON only with keys: "hook", "intro", "facts" (list of strings), "outro".
    '''
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        script_data = json.loads(response.choices[0].message.content)
        print("✅ Script Generated Successfully")
        return script_data
    except Exception as e:
        print(f"❌ Script Gen Failed: {e}")
        return None
