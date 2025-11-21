from gtts import gTTS
import os

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voice using Google TTS (Free)...")
    try:
        # Create directory if not exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        
        print("✅ Voice Generated Successfully")
        return output_path
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None
