#!/usr/bin/env python3
import os
import argparse
import logging
import sys
import json
import time
import random
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import setup_logging, load_config
from animal_selector import AnimalSelector
from content_generator import ContentGenerator
from youtube_uploader import YouTubeUploader

class SimpleVideoCreator:
    """منشئ فيديوهات مبسط بدون استخدام moviepy"""
    
    def create_long_video(self, content, voice_gender="male"):
        """إنشاء فيديو طويل (ملف وهمي للاختبار)"""
        try:
            output_dir = "outputs/videos"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_path = f"{output_dir}/{content['animal'].lower()}_long_{timestamp}.mp4"
            
            # إنشاء ملف فيديو وهمي
            with open(video_path, 'w') as f:
                f.write(f"VIDEO_CONTENT: {content['title']}\n")
                f.write(f"Animal: {content['animal']}\n")
                f.write(f"Duration: 3-5 minutes\n")
                f.write(f"Voice: {voice_gender}\n")
                f.write(f"Script: {content['script'][:200]}...\n")
            
            logging.info(f"✅ تم إنشاء فيديو طويل: {video_path}")
            logging.info(f"   العنوان: {content['title']}")
            logging.info(f"   الحيوان: {content['animal']}")
            logging.info(f"   الصوت: {voice_gender}")
            
            return video_path
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الفيديو الطويل: {e}")
            return None
    
    def create_short_video(self, content):
        """إنشاء شورت (ملف وهمي للاختبار)"""
        try:
            output_dir = "outputs/shorts"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_path = f"{output_dir}/{content['animal'].lower()}_short_{timestamp}.mp4"
            
            # إنشاء ملف شورت وهمي
            with open(video_path, 'w') as f:
                f.write(f"SHORT_CONTENT: {content['title']}\n")
                f.write(f"Animal: {content['animal']}\n")
                f.write(f"Duration: 15-60 seconds\n")
                f.write(f"Type: Music only (no voiceover)\n")
                f.write(f"Facts: {content['facts'][0]}\n")
            
            logging.info(f"✅ تم إنشاء شورت: {video_path}")
            logging.info(f"   العنوان: {content['title']}")
            logging.info(f"   الحيوان: {content['animal']}")
            logging.info(f"   النوع: موسيقى فقط")
            
            return video_path
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الشورت: {e}")
            return None

class YouTubeAutomation:
    def __init__(self):
        setup_logging()
        self.config = load_config()
        
        self.animal_selector = AnimalSelector()
        self.content_generator = ContentGenerator()
        self.video_creator = SimpleVideoCreator()
        self.youtube_uploader = YouTubeUploader()
        
        logging.info("✅ تم تهيئة النظام بالكامل")
        
    def run_test(self):
        """تشغيل تجريبي - فيديو واحد + شورت واحد"""
        try:
            logging.info("🎬 بدء التشغيل التجريبي")
            
            # إنشاء فيديو طويل واحد
            long_video = self._create_long_video()
            if long_video:
                logging.info("✅ تم إنشاء الفيديو الطويل")
            else:
                logging.error("❌ فشل إنشاء الفيديو الطويل")
                return False
            
            # إنشاء شورت واحد
            short_video = self._create_short_video()
            if short_video:
                logging.info("✅ تم إنشاء الشورت")
            else:
                logging.error("❌ فشل إنشاء الشورت")
                return False
            
            # رفع الفيديوهات
            videos_to_upload = []
            if long_video:
                videos_to_upload.append(long_video)
            if short_video:
                videos_to_upload.append(short_video)
                
            success = self._upload_videos(videos_to_upload)
            
            if success:
                logging.info("🎉 التشغيل التجريبي اكتمل بنجاح!")
                logging.info("📝 ملاحظة: الفيديوهات وهمية للاختبار، سيتم رفعها على اليوتيوب")
                return True
            else:
                logging.error("❌ فشل التشغيل التجريبي")
                return False
                
        except Exception as e:
            logging.error(f"❌ خطأ في التشغيل التجريبي: {e}")
            return False
    
    def run_daily_automation(self):
        """تشغيل يومي كامل - 2 فيديو طويل + 5 شورتات"""
        try:
            logging.info("🚀 بدء التشغيل اليومي الكامل")
            
            # إنشاء 2 فيديو طويل
            long_videos = []
            for i in range(2):
                video = self._create_long_video(voice_gender="male" if i % 2 == 0 else "female")
                if video:
                    long_videos.append(video)
                    logging.info(f"✅ فيديو طويل {i+1}: {video[1]['animal']}")
                else:
                    logging.error(f"❌ فشل إنشاء فيديو طويل {i+1}")
            
            # إنشاء 5 شورتات
            short_videos = []
            for i in range(5):
                short = self._create_short_video()
                if short:
                    short_videos.append(short)
                    logging.info(f"✅ شورت {i+1}: {short[1]['animal']}")
                else:
                    logging.error(f"❌ فشل إنشاء شورت {i+1}")
            
            # جمع جميع الفيديوهات للرفع
            all_videos = long_videos + short_videos
            
            if not all_videos:
                logging.error("❌ لم يتم إنشاء أي فيديوهات")
                return False
            
            # رفع الفيديوهات
            success = self._upload_videos(all_videos)
            
            if success:
                logging.info("🎉 التشغيل اليومي اكتمل بنجاح!")
                logging.info(f"📊 تم إنشاء {len(all_videos)} فيديو بنجاح")
                logging.info("📝 ملاحظة: الفيديوهات وهمية للاختبار، سيتم رفعها على اليوتيوب")
                return True
            else:
                logging.error("❌ فشل التشغيل اليومي")
                return False
                
        except Exception as e:
            logging.error(f"❌ خطأ في التشغيل اليومي: {e}")
            return False
    
    def _create_long_video(self, voice_gender="male"):
        """إنشاء فيديو طويل مع تعليق صوتي"""
        try:
            animal = self.animal_selector.get_animal()
            content = self.content_generator.generate_animal_content(animal, for_short=False)
            
            logging.info(f"🎬 إنشاء فيديو طويل عن: {animal}")
            logging.info(f"   🎙️ صوت: {voice_gender}")
            
            video_path = self.video_creator.create_long_video(content, voice_gender=voice_gender)
            
            if video_path and os.path.exists(video_path):
                logging.info(f"✅ تم إنشاء الفيديو الطويل: {video_path}")
                return (video_path, content)
            else:
                logging.error(f"❌ فشل إنشاء الفيديو الطويل")
                return None
                
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الفيديو الطويل: {e}")
            return None
    
    def _create_short_video(self):
        """إنشاء شورت مع موسيقى فقط"""
        try:
            animal = self.animal_selector.get_animal()
            content = self.content_generator.generate_animal_content(animal, for_short=True)
            
            logging.info(f"🎬 إنشاء شورت عن: {animal}")
            
            video_path = self.video_creator.create_short_video(content)
            
            if video_path and os.path.exists(video_path):
                logging.info(f"✅ تم إنشاء الشورت: {video_path}")
                return (video_path, content)
            else:
                logging.error(f"❌ فشل إنشاء الشورت")
                return None
                
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء الشورت: {e}")
            return None
    
    def _upload_videos(self, videos_data):
        """رفع الفيديوهات على اليوتيوب"""
        try:
            successful_uploads = 0
            
            for i, (video_path, content) in enumerate(videos_data, 1):
                logging.info(f"📤 رفع الفيديو {i}/{len(videos_data)}: {content['animal']}")
                
                if not os.path.exists(video_path):
                    logging.error(f"❌ ملف الفيديو غير موجود: {video_path}")
                    continue
                
                # رفع الفيديو
                video_id = self.youtube_uploader.upload_video(video_path, content)
                
                if video_id:
                    successful_uploads += 1
                    logging.info(f"✅ تم رفع الفيديو بنجاح: {video_id}")
                    
                    # إضافة تأخير بين الرفعات لتجنب حظر اليوتيوب
                    if i < len(videos_data):
                        logging.info("⏳ انتظار 10 ثانية قبل الرفع التالي...")
                        time.sleep(10)
                else:
                    logging.error(f"❌ فشل رفع الفيديو: {content['title']}")
            
            logging.info(f"📊 تم رفع {successful_uploads}/{len(videos_data)} فيديو بنجاح")
            return successful_uploads > 0
            
        except Exception as e:
            logging.error(f"❌ خطأ في رفع الفيديوهات: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="نظام أتمتة قناة يوتيوب للحيوانات")
    parser.add_argument("--test-run", action="store_true", help="تشغيل تجريبي - فيديو واحد + شورت واحد")
    parser.add_argument("--daily-run", action="store_true", help="تشغيل يومي كامل - 2 فيديو + 5 شورتات")
    
    args = parser.parse_args()
    
    automation = YouTubeAutomation()
    
    if args.test_run:
        success = automation.run_test()
    elif args.daily_run:
        success = automation.run_daily_automation()
    else:
        logging.info("🔍 لم يتم تحديد وضع التشغيل، استخدام الوضع التجريبي")
        success = automation.run_test()
    
    # الخروج بكود مناسب
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
