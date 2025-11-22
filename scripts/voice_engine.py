import asyncio
import edge_tts
import os

async def _generate_voice_async(text, output_path):
    # Voice: Male, Deep (Christopher)
    voice = "en-US-ChristopherNeural"
    # Rate: Default (0%) for longer duration and clarity
    rate = "+0%" 
    
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

def generate_voice(text, output_path="assets/temp/voice.mp3"):
    print("🎙️ Generating Voice (Normal Speed)...")
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        asyncio.run(_generate_voice_async(text, output_path))
        return output_path
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None
