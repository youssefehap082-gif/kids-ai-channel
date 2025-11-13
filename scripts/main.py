#!/usr/bin/env python3
import os
import argparse
import logging
import sys
from datetime import datetime

# إضافة المسار للوحدات
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from animal_selector import AnimalSelector
    from content_generator import ContentGenerator
    from video_creator import VideoCreator
    from youtube_uploader import YouTubeUploader
    from performance_analyzer import PerformanceAnalyzer
    from utils import setup_logging, load_config
except ImportError as e:
    print(f"Import error: {e}")
    # سنقوم بإنشاء فئات بديلة للاختبار
    pass

class YouTubeAutomation:
    def __init__(self):
        setup_logging()
        self.config = load_config()
        
        # تهيئة المكونات مع معالجة الأخطاء
        try:
            self.animal_selector = AnimalSelector()
            self.content_generator = ContentGenerator()
            self.video_creator = VideoCreator()
            self.youtube_uploader = YouTubeUploader()
            self.performance_analyzer = PerformanceAnalyzer()
        except Exception as e:
            logging.warning(f"Some components failed to initialize: {e}")
            # سنستخدم فئات بديلة للاختبار
            self.animal_selector = SimpleAnimalSelector()
            self.content_generator = SimpleContentGenerator()
        
    def run_daily_automation(self, test_run=False):
        """تشغيل النظام اليومي"""
        try:
            logging.info("🚀 بدء نظام أتمتة اليوتيوب")
            
            if test_run:
                logging.info("🎬 وضع الاختبار - إنشاء فيديو تجريبي واحد")
                return self._create_test_video()
            
            # تحليل الأداء أولاً
            try:
                self.performance_analyzer.analyze_performance()
            except Exception as e:
                logging.warning(f"Performance analysis skipped: {e}")
            
            # إنشاء الفيديوهات الطويلة (2 فيديو)
            long_videos = self._create_long_videos(2)
            
            # إنشاء الشورتس (5 شورتس)
            shorts = self._create_shorts(5)
            
            # رفع الفيديوهات
            self._upload_videos(long_videos + shorts)
            
            logging.info("✅ اكتملت العملية بنجاح")
            
        except Exception as e:
            logging.error(f"❌ خطأ في النظام: {e}")
            raise
            
    def _create_test_video(self):
        """إنشاء فيديو تجريبي"""
        logging.info("🎬 إنشاء فيديو تجريبي")
        
        animal = self.animal_selector.get_animal()
        logging.info(f"الحيوان المختار: {animal}")
        
        content = self.content_generator.generate_animal_content(animal)
        logging.info(f"المحتوى المُنشأ: {content['title']}")
        
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
                # في وضع الاختبار، لا نرفع فعلياً
                if os.getenv('TEST_MODE'):
                    logging.info(f"🎯 [اختبار] كان سيتم رفع: {content['title']}")
                    continue
                    
                video_id = self.youtube_uploader.upload_video(video_path, content)
                if video_id:
                    logging.info(f"✅ تم رفع الفيديو بنجاح: {video_id}")
                    # تسجيل البيانات للأداء
                    self.performance_analyzer.record_upload(content['animal'], video_id)
            except Exception as e:
                logging.error(f"❌ خطأ في رفع الفيديو: {e}")

# فئات بديلة للاختبار
class SimpleAnimalSelector:
    def get_animal(self):
        animals = ["Lion", "Elephant", "Tiger", "Giraffe", "Dolphin", "Eagle"]
        import random
        return random.choice(animals)

class SimpleContentGenerator:
    def generate_animal_content(self, animal, for_short=False):
        facts = [
            f"{animal}s are amazing creatures",
            f"They have unique characteristics",
            f"{animal}s play important roles in ecosystem",
            f"Their behavior is fascinating",
            f"They have adapted to their environment",
            f"{animal}s have special abilities",
            f"Their social structure is interesting",
            f"They face conservation challenges",
            f"{animal}s have existed for long time",
            f"They are important to biodiversity"
        ]
        
        title = f"Amazing Facts About {animal}s" if not for_short else f"{animal} Facts 🐾 #shorts"
        description = f"Learn about {animal}s in this educational video. Subscribe for more!"
        tags = [animal, "animals", "wildlife", "facts", "nature"]
        
        return {
            "animal": animal,
            "facts": facts,
            "script": f"Today we learn about {animal}. " + ". ".join(facts),
            "title": title,
            "description": description,
            "tags": tags,
            "is_short": for_short
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-run", action="store_true", help="تشغيل تجريبي")
    args = parser.parse_args()
    
    automation = YouTubeAutomation()
    automation.run_daily_automation(test_run=args.test_run)
