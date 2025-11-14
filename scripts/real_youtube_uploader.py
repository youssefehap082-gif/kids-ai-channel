import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

class RealYouTubeUploader:
    def __init__(self):
        self.setup_youtube_api()
        
    def setup_youtube_api(self):
        """إعداد اتصال YouTube API"""
        try:
            # استخدام credentials من environment variables
            credentials = Credentials(
                token=None,
                refresh_token=os.getenv('YT_REFRESH_TOKEN'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('YT_CLIENT_ID'),
                client_secret=os.getenv('YT_CLIENT_SECRET')
            )
            
            # طلب token جديد
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
            
            self.youtube = build('youtube', 'v3', credentials=credentials)
            logging.info("✅ تم الاتصال بنجاح مع YouTube API")
            
        except Exception as e:
            logging.error(f"❌ فشل الاتصال مع YouTube API: {e}")
            raise
    
    def upload_video(self, video_path, content):
        """رفع فيديو فعلي على اليوتيوب"""
        try:
            logging.info(f"🚀 بدء رفع الفيديو: {content['title']}")
            
            # إعداد بيانات الفيديو
            body = {
                'snippet': {
                    'title': content['title'],
                    'description': content['description'],
                    'tags': content['tags'],
                    'categoryId': '22'  # Education
                },
                'status': {
                    'privacyStatus': 'public',  # أو 'private' للاختبار
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # إنشاء media upload
            media = MediaFileUpload(
                video_path,
                chunksize=1024*1024,
                resumable=True
            )
            
            # طلب الرفع
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # تنفيذ الرفع
            response = self._resumable_upload(request)
            
            if response:
                video_id = response['id']
                logging.info(f"✅ تم رفع الفيديو بنجاح: https://youtu.be/{video_id}")
                return video_id
            else:
                logging.error("❌ فشل رفع الفيديو")
                return None
                
        except Exception as e:
            logging.error(f"❌ خطأ في رفع الفيديو: {e}")
            return None
    
    def _resumable_upload(self, request):
        """رفع قابل للاستئناف مع التعامل مع الأخطاء"""
        response = None
        retry = 0
        max_retries = 3
        
        while response is None and retry < max_retries:
            try:
                status, response = request.next_chunk()
                if status:
                    logging.info(f"📊 تم رفع {int(status.progress() * 100)}%")
            except Exception as e:
                if retry < max_retries - 1:
                    logging.warning(f"⚠️  إعادة محاولة الرفع ({retry + 1}/{max_retries}): {e}")
                    retry += 1
                else:
                    logging.error(f"❌ فشل الرفع بعد {max_retries} محاولات: {e}")
                    break
        
        return response
