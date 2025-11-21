
import os
from openai import OpenAI

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voice...")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: return None
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text
        )
        response.stream_to_file(output_path)
        return output_path
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None
