#!/usr/bin/env python3
import os
import argparse
import logging
import sys
import json
import time
from datetime import datetime

# إعداد المسارات
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import setup_logging, load_config

# استيراد الـ Uploader الجديد
from youtube_uploader import RealYouTubeUploader

class SimpleAnimalSelector:
    def get_animal(self):
        animals = ["Lion", "Elephant", "Tiger", "Giraffe", "Dolphin", "Eagle", "Penguin", "Kangaroo", "Wolf", "Bear"]
        import random
        animal = random.choice(animals)
        logging.info(f"🎯 تم اختيار الحيوان: {animal}")
        return animal

class SimpleContentGenerator:
    def generate_animal_content(self, animal, for_short=False):
        facts = [
            f"{animal}s are amazing creatures with unique adaptations that help them survive in their environments",
            f"They play crucial roles in their ecosystems, maintaining balance in nature's food chains",
            f"The habitat of {animal}s varies widely, from dense forests to open plains and deep oceans",
            f"Their diet is diverse, consisting of various plants, animals, or both depending on the species",
            f"{animal}s have fascinating social behaviors and complex communication methods",
            f"Conservation efforts are essential for protecting {animal}s from habitat loss and other threats",
            f"They possess remarkable physical characteristics and specialized abilities for survival",
            f"The reproduction cycle and family structures of {animal}s are fascinating to study",
            f"{animal}s have evolved over millions of years, adapting to changing environments",
            f"They contribute significantly to global biodiversity and ecological health"
        ]
        
        if for_short:
            title = f"Amazing {animal} Facts! 🐾 #shorts #animals"
            script = f"Discover {animal}s! {facts[0]} {facts[1]} Like and follow for daily animal content! 🐯"
        else:
            title = f"10 Incredible Facts About {animal}s | Wildlife Education Documentary"
            script = f"Welcome to our wildlife education channel! Today we're exploring the fascinating world of {animal}s. Here are 10 amazing facts: " + ". ".join([f"Number {i+1}: {fact}" for i, fact in enumerate(facts)]) + " Which fact surprised you most? Let us know in comments! Don't forget to subscribe for daily wildlife content!"
        
        description = f"Discover the amazing world of {animal}s in this educational wildlife video! "
        description += f"In this episode, we explore 10 fascinating facts about {animal}s, including their behavior, habitat, diet, and unique characteristics. "
        description += "Perfect for animal lovers, wildlife enthusiasts, and educational purposes.\n\n"
        description += "📚 What you'll learn in this video:\n"
        description += "• Amazing facts about " + animal + " behavior\n"
        description += "• Their natural habitats and environments\n"
        description += "• Diet and feeding patterns\n"
        description += "• Conservation status and importance\n"
        description += "• Unique physical characteristics\n\n"
        description += "🔔 Don't forget to:\n"
        description += "✅ SUBSCRIBE for daily animal facts\n"
        description += "🔔 Hit the BELL icon for notifications\n"
        description += "👍 LIKE if you learned something new\n"
        description += "💬 COMMENT your favorite fact below\n"
        description += "📤 SHARE with fellow animal lovers\n\n"
        description += "🏷️ Related tags: "
        description += f"#{animal}, #animals, #wildlife, #nature, #education, #animalfacts, #wildlifeeducation, #naturedocumentary, #animaldocumentary\n\n"
        description += "⚠️ Disclaimer: This content is educational and created for entertainment purposes."
        
        tags = [
            animal, "animals", "wildlife", "nature", "education", 
            "animal facts", "wildlife education", "nature documentary",
            "animal documentary", "facts about animals", "wildlife facts",
            animal.lower() + " facts", "educational video", "wildlife channel"
        ]
        
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
        """إنشاء فيديو طويل"""
        try:
            output_dir = "outputs/videos"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_path = f"{output_dir}/{content['animal'].lower()}_{timestamp}.mp4"
            
            # إنشاء فيديو تجريبي بسيط
            with open(video_path, 'w') as f:
                f.write(f"Simulated video file for: {content['title']}")
            
            logging.info(f"✅ تم إنشاء فيديو طويل: {video_path}")
            logging.info(f"   العنوان: {content['title']}")
            
            return video_path
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الفيديو الطويل: {e}")
            return None
    
    def create_short_video(self, content):
        """إنشاء شورت"""
        try:
            output_dir = "outputs/shorts"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            short_path = f"{output_dir}/{content['animal'].lower()}_short_{timestamp}.mp4"
            
            with open(short_path, 'w') as f:
                f.write(f"Simulated short video for: {content['title']}")
            
            logging.info(f"✅ تم إنشاء شورت: {short_path}")
            logging.info(f"   العنوان: {content['title']}")
            
            return short_path
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الشورت: {e}")
            return None

class SimpleYouTubeUploader:
    """نظام الرفع الاختباري"""
    
    def upload_video(self, video_path, content):
        """محاكاة رفع الفيديو"""
        try:
            logging.info(f"🎯 [وضع الاختبار] محاكاة رفع الفيديو:")
            logging.info(f"   📹 العنوان: {content['title']}")
            logging.info(f"   🐾 الحيوان: {content['animal']}")
            
            import random
            video_id = f"test_{content['animal'].lower()}_{random.randint(1000,9999)}"
            
            logging.info(f"✅ [اختبار] تم محاكاة رفع الفيديو بنجاح!")
            logging.info(f"   🆔 معرّف محاكاة: {video_id}")
            
            return video_id
            
        except Exception as e:
            logging.error(f"❌ خطأ في محاكاة الرفع: {e}")
            return None

class PerformanceAnalyzer:
    """تحليل الأداء"""
    
    def analyze_performance(self):
        logging.info("📊 تحليل أداء الفيديوهات...")
    
    def record_upload(self, animal, video_id):
        logging.info(f"📝 تسجيل رفع: {animal} - {video_id}")

class YouTubeAutomation:
    def __init__(self, real_upload=False):
        setup_logging()
        self.config = load_config()
        self.real_upload = real_upload
        
        logging.info(f"🎯 وضع التشغيل: {'رفع فعلي على اليوتيوب' if real_upload else 'اختبار'}")
        
        # تهيئة المكونات
        self.animal_selector = SimpleAnimalSelector()
        self.content_generator = SimpleContentGenerator()
        self.video_creator = SimpleVideoCreator()
        
        # اختيار نظام الرفع المناسب - هذا هو التحديث المطلوب
        if real_upload:
            self.youtube_uploader = RealYouTubeUploader()
        else:
            self.youtube_uploader = SimpleYouTubeUploader()
            
        self.performance_analyzer = PerformanceAnalyzer()
        
    def run_daily_automation(self, test_run=False):
        """تشغيل النظام اليومي"""
        try:
            logging.info("🚀 بدء نظام أتمتة اليوتيوب")
            
            if test_run:
                logging.info("🎬 تشغيل تجريبي - فيديو واحد")
                videos_data = self._create_test_video()
            else:
                logging.info("📅 تشغيل يومي كامل")
                self.performance_analyzer.analyze_performance()
                long_videos = self._create_long_videos(2)
                shorts = self._create_shorts(5)
                videos_data = long_videos + shorts
            
            # رفع الفيديوهات
            successful_uploads = self._upload_videos(videos_data)
            
            # التحقق النهائي من النجاح
            if successful_uploads > 0:
                logging.info(f"🎉 اكتملت العملية بنجاح! {successful_uploads}/{len(videos_data)} فيديوهات مرفوعة فعلياً على اليوتيوب")
                return True
            else:
                logging.error(f"❌ فشل العملية - لم يتم رفع أي فيديو على اليوتيوب")
                return False
            
        except Exception as e:
            logging.error(f"❌ خطأ في النظام: {e}")
            return False
            
    def _create_test_video(self):
        """إنشاء فيديو تجريبي"""
        logging.info("🎬 إنشاء فيديو تجريبي...")
        
        animal = self.animal_selector.get_animal()
        content = self.content_generator.generate_animal_content(animal)
        video_path = self.video_creator.create_long_video(content, voice_gender="male")
        
        if video_path:
            logging.info(f"✅ تم إنشاء الفيديو التجريبي")
            return [(video_path, content)]
        else:
            logging.error("❌ فشل إنشاء الفيديو التجريبي")
            return []
    
    def _create_long_videos(self, count):
        """إنشاء الفيديوهات الطويلة"""
        videos = []
        for i in range(count):
            try:
                gender = "male" if i % 2 == 0 else "female"
                animal = self.animal_selector.get_animal()
                content = self.content_generator.generate_animal_content(animal)
                video_path = self.video_creator.create_long_video(content, voice_gender=gender)
                if video_path:
                    videos.append((video_path, content))
                    logging.info(f"✅ فيديو طويل {i+1}: {animal}")
                else:
                    logging.error(f"❌ فشل إنشاء فيديو طويل {i+1}")
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
                if short_path:
                    shorts.append((short_path, content))
                    logging.info(f"✅ شورت {i+1}: {animal}")
                else:
                    logging.error(f"❌ فشل إنشاء شورت {i+1}")
            except Exception as e:
                logging.error(f"❌ فشل إنشاء شورت {i+1}: {e}")
        return shorts
    
    def _upload_videos(self, videos_data):
        """رفع الفيديوهات لليوتيوب"""
        successful_uploads = 0
        
        for i, (video_path, content) in enumerate(videos_data, 1):
            try:
                logging.info(f"📤 رفع الفيديو {i}/{len(videos_data)}...")
                
                # التحقق من وجود الملف
                if not os.path.exists(video_path):
                    logging.warning(f"⚠️ الملف غير موجود: {video_path}")
                    continue
                
                # رفع الفيديو
                video_id = self.youtube_uploader.upload_video(video_path, content)
                
                if video_id:
                    successful_uploads += 1
                    logging.info(f"✅ تم رفع الفيديو بنجاح على اليوتيوب!")
                    self.performance_analyzer.record_upload(content['animal'], video_id)
                else:
                    logging.error(f"❌ فشل رفع الفيديو: {content['title']}")
                    
            except Exception as e:
                logging.error(f"❌ خطأ في رفع الفيديو {i}: {e}")
        
        return successful_uploads

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="نظام أتمتة قناة يوتيوب للحيوانات")
    parser.add_argument("--test-run", action="store_true", help="تشغيل تجريبي - فيديو واحد")
    parser.add_argument("--real-upload", action="store_true", help="رفع فعلي على اليوتيوب")
    parser.add_argument("--daily-run", action="store_true", help="تشغيل يومي كامل")
    args = parser.parse_args()
    
    # تحديد نوع التشغيل
    if args.real_upload:
        automation = YouTubeAutomation(real_upload=True)
        success = automation.run_daily_automation(test_run=args.test_run)
        # الخروج بكود خطأ إذا فشل الرفع
        sys.exit(0 if success else 1)
    else:
        automation = YouTubeAutomation(real_upload=False)
        automation.run_daily_automation(test_run=args.test_run)
