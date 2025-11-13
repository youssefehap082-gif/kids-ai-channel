import logging
import random

class SimpleYouTubeUploader:
    """نظام الرفع الاختباري"""
    
    def upload_video(self, video_path, content):
        """محاكاة رفع الفيديو"""
        try:
            logging.info(f"🎯 [وضع الاختبار] محاكاة رفع الفيديو:")
            logging.info(f"   📹 العنوان: {content['title']}")
            logging.info(f"   🐾 الحيوان: {content['animal']}")
            
            video_id = f"test_{content['animal'].lower()}_{random.randint(1000,9999)}"
            
            logging.info(f"✅ [اختبار] تم محاكاة رفع الفيديو بنجاح!")
            logging.info(f"   🆔 معرّف محاكاة: {video_id}")
            
            return video_id
            
        except Exception as e:
            logging.error(f"❌ خطأ في محاكاة الرفع: {e}")
            return None
