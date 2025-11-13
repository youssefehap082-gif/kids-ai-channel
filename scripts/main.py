#!/usr/bin/env python3
import os
import argparse
import logging
import sys
import json
from datetime import datetime

# إضافة المسار للوحدات
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# إعداد التسجيل أولاً
def setup_logging():
    """إعداد نظام التسجيل"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/automation.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.info("=== بدء النظام ===")

def load_config():
    """تحميل الإعدادات"""
    return {
        "max_videos_per_day": 2,
        "max_shorts_per_day": 5,
        "video_duration": {"min": 180, "max": 600},
        "short_duration": {"min": 15, "max": 60},
        "target_languages": ["en", "es", "fr", "de", "ar"],
        "test_mode": True
    }

# فئات بديلة للاختبار
class SimpleAnimalSelector:
    def get_animal(self):
        animals = ["Lion", "Elephant", "Tiger", "Giraffe", "Dolphin", "Eagle", "Penguin", "Kangaroo"]
        import random
        animal = random.choice(animals)
        logging.info(f"تم اختيار الحيوان: {animal}")
        return animal

class SimpleContentGenerator:
    def generate_animal_content(self, animal, for_short=False):
        facts = [
            f"{animal}s are amazing creatures with unique adaptations",
            f"They play crucial roles in their ecosystems and food chains",
            f"The habitat of {animal}s is diverse across different regions",
            f"Their diet consists of various plants and/or animals",
            f"{animal}s have fascinating social behaviors and communication",
            f"Conservation efforts are important for protecting {animal}s",
            f"They have remarkable physical characteristics and abilities",
            f"The reproduction cycle of {animal}s is interesting to study",
            f"{animal}s have evolved over millions of years",
            f"They contribute significantly to biodiversity on our planet"
        ]
        
        if for_short:
            title = f"Amazing {animal} Facts! 🐾 #shorts"
            script = f"Quick {animal} facts! {facts[0]} {facts[1]} Like and follow for more!"
        else:
            title = f"10 Incredible Facts About {animal}s | Wildlife Education"
            script = f"Welcome to our wildlife channel! Today we explore {animal}s. " + ". ".join([f"Fact {i+1}: {fact}" for i, fact in enumerate(facts)]) + " Thanks for watching! Don't forget to subscribe!"
        
        description = f"Learn fascinating facts about {animal}s in this educational video. "
        description += f"Discover their behavior, habitat, diet, and unique characteristics. "
        description += "Perfect for animal lovers and wildlife enthusiasts!\n\n"
        description += "Don't forget to:\n"
        description += "✅ Subscribe for daily animal content\n"
        description += "🔔 Hit the bell icon for notifications\n"
        description += "👍 Like this video if you learned something new\n"
        description += "💬 Comment your favorite fact below\n\n"
        description += f"#{animal} #animals #wildlife #nature #education #facts"
        
        tags = [animal, "animals", "wildlife", "nature", "education", "animal facts", "wildlife education", "nature documentary"]
        
        return {
            "animal": animal,
            "facts": facts,
            "script": script,
            "title": title,
            "description": description,
            "tags": tags,
            "is_short": for_short
        }

class SimpleVideoCreator:
    def create_long_video(self, content, voice_gender="male"):
        """إنشاء فيديو طويل بسيط (بدون معالجة فيديو حقيقية في الاختبار)"""
        try:
            # في البيئة الاختبارية، ننشئ ملف فيديو وهمي
            output_dir = "outputs/videos"
            os.makedirs(output_dir, exist_ok=True)
            
            video_path = f"{output_dir}/{content['animal'].lower()}_video.mp4"
            
            # إنشاء ملف فيديو وهمي للاختبار
            with open(video_path, 'w') as f:
                f.write("This is a simulated video file for testing")
            
            logging.info(f"✅ تم إنشاء فيديو وهمي: {video_path}")
            return video_path
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الفيديو: {e}")
            return f"outputs/videos/fallback_{content['animal']}.mp4"
    
    def create_short_video(self, content):
        """إنشاء شورت بسيط"""
        try:
            output_dir = "outputs/shorts"
            os.makedirs(output_dir, exist_ok=True)
            
            short_path = f"{output_dir}/{content['animal'].lower()}_short.mp4"
            
            # إنشاء ملف شورت وهمي للاختبار
            with open(short_path, 'w') as f:
                f.write("This is a simulated short video for testing")
            
            logging.info(f"✅ تم إنشاء شورت وهمي: {short_path}")
            return short_path
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الشورت: {e}")
            return f"outputs/shorts/fallback_{content['animal']}_short.mp4"

class SimpleYouTubeUploader:
    def upload_video(self, video_path, content):
        """محاكاة رفع الفيديو في وضع الاختبار"""
        logging.info(f"🎯 [وضع الاختبار] كان سيتم رفع الفيديو: {content['title']}")
        logging.info(f"🎯 المسار: {video_path}")
        logging.info(f"🎯 الوصف: {content['description'][:100]}...")
        return f"test_video_{content['animal'].lower()}"

class SimplePerformanceAnalyzer:
    def analyze_performance(self):
        logging.info("📊 تحليل الأداء (وضع الاختبار)")
    
    def record_upload(self, animal, video_id):
        logging.info(f"📝 تسجيل رفع: {animal} - {video_id}")

class YouTubeAutomation:
    def __init__(self):
        setup_logging()  # يجب استدعاء هذه الدالة أولاً
        self.config = load_config()
        
        # تهيئة المكونات البسيطة للاختبار
        logging.info("🔧 تهيئة النظام في وضع الاختبار...")
        self.animal_selector = SimpleAnimalSelector()
        self.content_generator = SimpleContentGenerator()
        self.video_creator = SimpleVideoCreator()
        self.youtube_uploader = SimpleYouTubeUploader()
        self.performance_analyzer = SimplePerformanceAnalyzer()
        
    def run_daily_automation(self, test_run=False):
        """تشغيل النظام اليومي"""
        try:
            logging.info("🚀 بدء نظام أتمتة اليوتيوب")
            
            if test_run:
                logging.info("🎬 وضع الاختبار - إنشاء فيديو تجريبي واحد")
                return self._create_test_video()
            
            # في التشغيل العادي
            self.performance_analyzer.analyze_performance()
            long_videos = self._create_long_videos(2)
            shorts = self._create_shorts(5)
            self._upload_videos(long_videos + shorts)
            
            logging.info("✅ اكتملت العملية بنجاح")
            
        except Exception as e:
            logging.error(f"❌ خطأ في النظام: {e}")
            raise
            
    def _create_test_video(self):
        """إنشاء فيديو تجريبي"""
        logging.info("🎬 إنشاء فيديو تجريبي")
        
        animal = self.animal_selector.get_animal()
        content = self.content_generator.generate_animal_content(animal)
        video_path = self.video_creator.create_long_video(content, voice_gender="male")
        
        logging.info(f"✅ تم إنشاء الفيديو التجريبي: {video_path}")
        return [(video_path, content)]
    
    def _create_long_videos(self, count):
        """إنشاء الفيديوهات الطويلة"""
        videos = []
        for i in range(count):
            try:
                gender = "male" if i % 2 == 0 else "female"
                animal = self.animal_selector.get_animal()
                content = self.content_generator.generate_animal_content(animal)
                video_path = self.video_creator.create_long_video(content, voice_gender=gender)
                videos.append((video_path, content))
                logging.info(f"✅ تم إنشاء فيديو طويل {i+1}: {animal}")
            except Exception as e:
                logging.error(f"❌ فشل إنشاء فيديو طويل {i+1}: {e}")
        return videos
    
    def _create_shorts(self, count):
        """إنشاء الشورتس"""
        shorts = []
        for i in range(count):
            try:
                animal = self.animal_selector.get_animal()
                content = self.content_generator.generate_animal_content(animal, for_short=True)
                short_path = self.video_creator.create_short_video(content)
                shorts.append((short_path, content))
                logging.info(f"✅ تم إنشاء شورت {i+1}: {animal}")
            except Exception as e:
                logging.error(f"❌ فشل إنشاء شورت {i+1}: {e}")
        return shorts
    
    def _upload_videos(self, videos_data):
        """رفع الفيديوهات لليوتيوب"""
        for video_path, content in videos_data:
            try:
                video_id = self.youtube_uploader.upload_video(video_path, content)
                if video_id:
                    logging.info(f"✅ تم رفع الفيديو بنجاح: {video_id}")
                    self.performance_analyzer.record_upload(content['animal'], video_id)
            except Exception as e:
                logging.error(f"❌ خطأ في رفع الفيديو: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-run", action="store_true", help="تشغيل تجريبي")
    args = parser.parse_args()
    
    automation = YouTubeAutomation()
    automation.run_daily_automation(test_run=args.test_run)
