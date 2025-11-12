import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save

# 1. حط مفتاح ElevenLabs API بتاعك هنا
ELEVEN_API_KEY = "YOUR_ELEVENLABS_API_KEY"

# 2. النص اللي عايز تحوله لصوت
TEXT_TO_SPEAK = "Hello, this is a free voiceover test. Welcome to my channel!"

# 3. اسم الملف اللي هيتحفظ
OUTPUT_FILENAME = "generated_voiceover.mp3"

def create_free_voiceover():
    if ELEVEN_API_KEY == "YOUR_ELEVENLABS_API_KEY":
        print("خطأ: لازم تحط ElevenLabs API Key بتاعك الأول!")
        return

    try:
        client = ElevenLabs(api_key=ELEVEN_API_KEY)
        
        print("جاري تحويل النص إلى صوت...")
        
        # 4. طلب إنشاء الصوت
        audio = client.generate(
            text=TEXT_TO_SPEAK,
            voice="Rachel",  # ده اسم صوت مجاني (ممكن تغيره لـ "Adam" أو "Bella")
            model="eleven_multilingual_v2" # موديل بيدعم لغات كتير
        )
        
        # 5. حفظ الملف الصوتي
        save(audio, OUTPUT_FILENAME)
        
        print(f"تم حفظ التعليق الصوتي بنجاح في ملف: {OUTPUT_FILENAME}")

    except Exception as e:
        print(f"حصلت مشكلة: {e}")

if __name__ == "__main__":
    create_free_voiceover()
