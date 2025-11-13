import os
import requests
import logging
from pydub import AudioSegment

class VoiceGenerator:
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVEN_API_KEY")
        
    def generate_voiceover(self, text, voice_gender="male", output_file=None):
        """إنشاء تعليق صوتي احترافي"""
        try:
            if not output_file:
                output_file = f"outputs/temp/voiceover_{os.urandom(4).hex()}.mp3"
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            if self.elevenlabs_api_key:
                return self._generate_elevenlabs_voice(text, voice_gender, output_file)
            else:
                return self._generate_fallback_voice(text, output_file)
                
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء التعليق الصوتي: {e}")
            return self._generate_fallback_voice(text, output_file)
    
    def _generate_elevenlabs_voice(self, text, voice_gender, output_file):
        """استخدام Eleven Labs للصوت عالي الجودة"""
        try:
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
                    "similarity_boost": 0.8,
                    "style": 0.7,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                logging.info(f"✅ تم إنشاء تعليق صوتي: {output_file}")
                return output_file
            else:
                logging.error(f"❌ خطأ ElevenLabs: {response.status_code}")
                return self._generate_fallback_voice(text, output_file)
                
        except Exception as e:
            logging.error(f"❌ خطأ في ElevenLabs: {e}")
            return self._generate_fallback_voice(text, output_file)
    
    def _generate_fallback_voice(self, text, output_file):
        """نسخة احتياطية للصوت"""
        try:
            # استخدام gTTS كبديل مجاني
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_file)
            
            logging.info(f"✅ تم إنشاء تعليق صوتي احتياطي: {output_file}")
            return output_file
            
        except Exception as e:
            logging.error(f"❌ خطأ في التعليق الصوتي الاحتياطي: {e}")
            
            # إنشاء ملف صوتي صامت كحل أخير
            silent_audio = AudioSegment.silent(duration=30000)  # 30 ثانية صمت
            silent_audio.export(output_file, format="mp3")
            
            return output_file
