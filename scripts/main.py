#!/usr/bin/env python3
import os
import argparse
import logging
from datetime import datetime, timedelta
from animal_selector import AnimalSelector
from content_generator import ContentGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from performance_analyzer import PerformanceAnalyzer
from utils import setup_logging, load_config

class YouTubeAutomation:
    def __init__(self):
        setup_logging()
        self.config = load_config()
        self.animal_selector = AnimalSelector()
        self.content_generator = ContentGenerator()
        self.video_creator = VideoCreator()
        self.youtube_uploader = YouTubeUploader()
        self.performance_analyzer = PerformanceAnalyzer()
        
    def run_daily_automation(self, test_run=False):
        """تشغيل النظام اليومي"""
        try:
            logging.info("🚀 بدء نظام أتمتة اليوتيوب")
            
            if test_run:
                return self._create_test_video()
            
            # تحليل الأداء أولاً
            self.performance_analyzer.analyze_performance()
            
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
        content = self.content_generator.generate_animal_content(animal)
        video_path = self.video_creator.create_long_video(content, voice_gender="male")
        
        # رفع تجريبي (يمكن تعطيله للاختبار)
        # self.youtube_uploader.upload_video(video_path, content)
        
        logging.info(f"✅ تم إنشاء الفيديو التجريبي: {video_path}")
        return [video_path]
    
    def _create_long_videos(self, count):
        """إنشاء الفيديوهات الطويلة"""
        videos = []
        for i in range(count):
            gender = "male" if i % 2 == 0 else "female"
            animal = self.animal_selector.get_animal()
            content = self.content_generator.generate_animal_content(animal)
            video_path = self.video_creator.create_long_video(content, voice_gender=gender)
            videos.append((video_path, content))
        return videos
    
    def _create_shorts(self, count):
        """إنشاء الشورتس"""
        shorts = []
        for i in range(count):
            animal = self.animal_selector.get_animal()
            content = self.content_generator.generate_animal_content(animal, for_short=True)
            short_path = self.video_creator.create_short_video(content)
            shorts.append((short_path, content))
        return shorts
    
    def _upload_videos(self, videos_data):
        """رفع الفيديوهات لليوتيوب"""
        for video_path, content in videos_data:
            try:
                video_id = self.youtube_uploader.upload_video(video_path, content)
                if video_id:
                    logging.info(f"✅ تم رفع الفيديو بنجاح: {video_id}")
                    # تسجيل البيانات للأداء
                    self.performance_analyzer.record_upload(content['animal'], video_id)
            except Exception as e:
                logging.error(f"❌ خطأ في رفع الفيديو: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-run", action="store_true", help="تشغيل تجريبي")
    args = parser.parse_args()
    
    automation = YouTubeAutomation()
    automation.run_daily_automation(test_run=args.test_run)
