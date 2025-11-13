import logging
import os

class SimpleYouTubeUploader:
    """محاكي رفع اليوتيوب للاختبار"""
    
    def upload_video(self, video_path, content):
        """محاكاة رفع الفيديو في وضع الاختبار"""
        try:
            logging.info(f"🎯 [وضع الاختبار] كان سيتم رفع الفيديو:")
            logging.info(f"   📹 العنوان: {content['title']}")
            logging.info(f"   🏷️ الحيوان: {content['animal']}")
            logging.info(f"   📁 الملف: {video_path}")
            logging.info(f"   📝 الوصف: {content['description'][:100]}...")
            logging.info(f"   🏷️ التاغات: {', '.join(content['tags'][:3])}...")
            
            # محاكاة ID فيديو
            import random
            video_id = f"test_{content['animal'].lower()}_{random.randint(1000,9999)}"
            
            logging.info(f"✅ [اختبار] تم محاكاة رفع الفيديو: {video_id}")
            return video_id
            
        except Exception as e:
            logging.error(f"❌ خطأ في محاكاة الرفع: {e}")
            return None
