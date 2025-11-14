import os
import logging
import time
from datetime import datetime

class YouTubeUploader:
    def __init__(self):
        self.setup_youtube_api()
    
    def setup_youtube_api(self):
        """إعداد اتصال YouTube API"""
        try:
            import google.oauth2.credentials
            import googleapiclient.discovery
            
            # التحقق من وجود بيانات الاعتماد
            required_vars = ['YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN']
            if not all(os.getenv(var) for var in required_vars):
                logging.error("❌ بيانات اعتماد YouTube غير مكتملة")
                self.youtube = None
                return
            
            credentials = google.oauth2.credentials.Credentials(
                token=None,
                refresh_token=os.getenv('YT_REFRESH_TOKEN'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('YT_CLIENT_ID'),
                client_secret=os.getenv('YT_CLIENT_SECRET')
            )
            
            self.youtube = googleapiclient.discovery.build(
                'youtube', 'v3', credentials=credentials)
            
            logging.info("✅ تم إعداد YouTube API بنجاح")
            
        except Exception as e:
            logging.error(f"❌ فشل إعداد YouTube API: {e}")
            self.youtube = None
    
    def upload_video(self, video_path, content):
        """رفع فيديو على اليوتيوب"""
        try:
            if self.youtube is None:
                logging.error("❌ خدمة YouTube غير متوفرة")
                return None
            
            if not os.path.exists(video_path):
                logging.error(f"❌ ملف الفيديو غير موجود: {video_path}")
                return None
            
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
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False,
                    'madeForKids': False
                }
            }
            
            # إذا كان شورت، نضيف إعدادات خاصة
            if content['is_short']:
                body['status']['madeForKids'] = False
                # إضافة #shorts للتأكد من التعرف عليه كشورت
                if '#shorts' not in body['snippet']['description']:
                    body['snippet']['description'] = f"{body['snippet']['description']}\n\n#shorts"
            
            from googleapiclient.http import MediaFileUpload
            
            # إنشاء طلب الرفع
            media = MediaFileUpload(
                video_path,
                chunksize=1024*1024,
                resumable=True,
                mimetype='video/mp4'
            )
            
            # إرسال طلب الرفع
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # تنفيذ الرفع
            response = self._resumable_upload(request)
            
            if response and 'id' in response:
                video_id = response['id']
                logging.info(f"✅ تم رفع الفيديو بنجاح!")
                logging.info(f"   🆔 معرّف الفيديو: {video_id}")
                logging.info(f"   🔗 الرابط: https://youtube.com/watch?v={video_id}")
                return video_id
            else:
                logging.error("❌ فشل رفع الفيديو")
                return None
                
        except Exception as e:
            logging.error(f"❌ خطأ في رفع الفيديو: {e}")
            return None
    
    def _resumable_upload(self, request):
        """رفع قابل للاستئناف"""
        response = None
        retry = 0
        max_retries = 3
        
        while response is None and retry < max_retries:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logging.info(f"📊 تم رفع {progress}%")
            except Exception as e:
                if retry < max_retries - 1:
                    logging.warning(f"⚠️ إعادة محاولة الرفع ({retry + 1}/{max_retries}): {e}")
                    retry += 1
                    time.sleep(5)
                else:
                    logging.error(f"❌ فشل الرفع بعد {max_retries} محاولات: {e}")
                    break
                    
        return response
