import os
import requests
from pydub import AudioSegment
import io

class VoiceGenerator:
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVEN_API_KEY")
        
    def generate_voiceover(self, text, voice_gender="male", output_file="voiceover.mp3"):
        """إنشاء تعليق صوتي"""
        try:
            if self.elevenlabs_api_key:
                return self._generate_elevenlabs_voice(text, voice_gender, output_file)
            else:
                return self._generate_fallback_voice(text, output_file)
        except Exception as e:
            print(f"Voice generation error: {e}")
            return self._generate_fallback_voice(text, output_file)
    
    def _generate_elevenlabs_voice(self, text, voice_gender, output_file):
        """استخدام Eleven Labs للصوت عالي الجودة"""
        voice_id = "21m00Tcm4TlvDq8ikWAM" if voice_gender == "female" else "VR6AewLTigWG4xSOukaG"
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return output_file
        else:
            raise Exception(f"ElevenLabs API error: {response.status_code}")
    
    def _generate_fallback_voice(self, text, output_file):
        """نسخة احتياطية للصوت (يمكن استخدام pyttsx3 محلياً)"""
        # هنا يمكنك استخدام مكتبة محلية للtext-to-speech
        # هذا مثال بسيط - تحتاج لتثبيت pyttsx3
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            return output_file
        except:
            # إنشاء ملف صوتي صامت كحل أخير
            silent_audio = AudioSegment.silent(duration=30000)  # 30 ثانية صمت
            silent_audio.export(output_file, format="mp3")
            return output_file
