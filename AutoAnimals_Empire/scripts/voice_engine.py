
import os
import requests
from openai import OpenAI

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voiceover...")
    
    eleven_key = os.environ.get("ELEVENLABS_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    # 1. Try ElevenLabs (Best Quality)
    if eleven_key:
        try:
            # Adam Voice ID (Popular viral voice)
            voice_id = "pNInz6obpgDQGcFmaJgB" 
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
            r = requests.post(url, json=data, headers=headers)
            if r.status_code == 200:
                with open(output_path, 'wb') as f: f.write(r.content)
                print("✅ Voice generated (ElevenLabs)")
                return output_path
        except Exception as e:
            print(f"⚠️ ElevenLabs Failed: {e}")

    # 2. Fallback to OpenAI TTS
    if openai_key:
        try:
            client = OpenAI(api_key=openai_key)
            response = client.audio.speech.create(
                model="tts-1",
                voice="onyx", # Deep male voice
                input=text
            )
            response.stream_to_file(output_path)
            print("✅ Voice generated (OpenAI Fallback)")
            return output_path
        except Exception as e:
            print(f"❌ OpenAI TTS Failed: {e}")
            
    return None
