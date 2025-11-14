#!/usr/bin/env python3
import os
import logging
import time
import requests
from datetime import datetime

class RealYouTubeUploader:
    """نظام الرفع الفعلي على اليوتيوب - الإصدار النهائي"""
    
    def __init__(self):
        self.setup_youtube_api()
        self.access_token = None
        self.token_expiry = None
    
    def setup_youtube_api(self):
        """إعداد اتصال YouTube API"""
        try:
            import google.oauth2.credentials
            import googleapiclient.discovery
            
            # التحقق من وجود جميع المتطلبات
            required_env_vars = ['YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN']
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            
            if missing_vars:
                logging.error(f"❌ متغيرات البيئة المفقودة: {missing_vars}")
                self.youtube = None
                return
            
            logging.info("🔧 التحقق من صحة الـ Credentials...")
            
            # الحصول على Access Token جديد
            self.access_token = self._get_new_access_token()
            if not self.access_token:
                logging.error("❌ فشل الحصول على Access Token")
                self.youtube = None
                return
            
            # إنشاء credentials باستخدام الـ Access Token
            credentials = google.oauth2.credentials.Credentials(
                token=self.access_token,
                refresh_token=os.getenv('YT_REFRESH_TOKEN'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('YT_CLIENT_ID'),
                client_secret=os.getenv('YT_CLIENT_SECRET')
            )
            
            # بناء خدمة YouTube
            self.youtube = googleapiclient.discovery.build(
                'youtube', 'v3', credentials=credentials)
            
            logging.info("✅ تم إعداد YouTube API بنجاح")
            
        except Exception as e:
            logging.error(f"❌ فشل إعداد YouTube API: {e}")
            self.youtube = None
    
    def _get_new_access_token(self):
        """الحصول على Access Token جديد"""
        try:
            client_id = os.getenv('YT_CLIENT_ID')
            client_secret = os.getenv('YT_CLIENT_SECRET')
            refresh_token = os.getenv('YT_REFRESH_TOKEN')
            
            if not client_id or not client_secret or not refresh_token:
                logging.error("❌ بيانات المصادقة غير مكتملة")
                return None
            
            url = 'https://oauth2.googleapis.com/token'
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            logging.info("🔄 إرسال طلب تجديد الـ Token...")
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if 'access_token' in result:
                # حساب وقت انتهاء الصلاحية (ساعة من الآن)
                self.token_expiry = datetime.now().timestamp() + 3500
                logging.info("✅ تم تجديد Access Token بنجاح")
                return result['access_token']
            else:
                error_msg = result.get('error', 'Unknown error')
                error_desc = result.get('error_description', 'No description')
                logging.error(f"❌ فشل تجديد Access Token: {error_msg} - {error_desc}")
                return None
                
        except Exception as e:
            logging.error(f"❌ خطأ في تجديد Access Token: {e}")
            return None
    
    def _ensure_valid_token(self):
        """التأكد من أن الـ Token صالح"""
        if not self.access_token or not self.token_expiry or datetime.now().timestamp() > self.token_expiry:
            logging.info("🔄 تجديد الـ Token...")
            self.access_token = self._get_new_access_token()
            if self.access_token:
                # إعادة بناء خدمة YouTube بالـ Token الجديد
                try:
                    import google.oauth2.credentials
                    import googleapiclient.discovery
                    credentials = google.oauth2.credentials.Credentials(
                        token=self.access_token,
                        refresh_token=os.getenv('YT_REFRESH_TOKEN'),
                        token_uri='https://oauth2.googleapis.com/token',
                        client_id=os.getenv('YT_CLIENT_ID'),
                        client_secret=os.getenv('YT_CLIENT_SECRET')
                    )
                    self.youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
                    return True
                except Exception as e:
                    logging.error(f"❌ خطأ في إعادة بناء خدمة YouTube: {e}")
                    return False
            else:
                return False
        return True
    
    def upload_video(self, video_path, content):
        """رفع فيديو فعلي على اليوتيوب"""
        try:
            # التأكد من أن الـ Token صالح
            if not self._ensure_valid_token():
                logging.error("❌ Token غير صالح - فشل الرفع")
                return None
            
            if self.youtube is None:
                logging.error("❌ خدمة YouTube غير متوفرة")
                return None
            
            if not os.path.exists(video_path):
                logging.error(f"❌ ملف الفيديو غير موجود: {video_path}")
                return None
            
            logging.info(f"🚀 بدء رفع الفيديو على اليوتيوب...")
            logging.info(f"   📹 العنوان: {content['title']}")
            logging.info(f"   🐾 الحيوان: {content['animal']}")
            
            # إعداد بيانات الفيديو
            body = {
                'snippet': {
                    'title': content['title'],
                    'description': content['description'],
                    'tags': content['tags'],
                    'categoryId': '22'  # Education
                },
                'status': {
                    'privacyStatus': 'public',  # فيديو عام
                    'selfDeclaredMadeForKids': False
                }
            }
            
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
                logging.info(f"🎉 تم رفع الفيديو بنجاح على اليوتيوب!")
                logging.info(f"   🆔 معرّف الفيديو: {video_id}")
                logging.info(f"   🔗 الرابط: https://youtube.com/watch?v={video_id}")
                
                # اعتبار الرفع ناجحاً - الفيديو مرفوع فعلياً
                logging.info(f"✅ تأكيد الرفع الناجح!")
                return video_id
            else:
                logging.error("❌ فشل رفع الفيديو - لا يوجد استجابة من YouTube")
                return None
                
        except Exception as e:
            logging.error(f"❌ خطأ في رفع الفيديو: {str(e)}")
            # محاولة تجديد الـ Token وإعادة المحاولة مرة واحدة
            if "token" in str(e).lower() or "auth" in str(e).lower():
                logging.info("🔄 محاولة تجديد الـ Token وإعادة الرفع...")
                self.access_token = None
                self.token_expiry = None
                return self.upload_video(video_path, content)
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
                elif response is not None:
                    break
            except Exception as e:
                if retry < max_retries - 1:
                    logging.warning(f"⚠️ إعادة محاولة الرفع ({retry + 1}/{max_retries}): {e}")
                    retry += 1
                    time.sleep(2)
                else:
                    logging.error(f"❌ فشل الرفع بعد {max_retries} محاولات: {e}")
                    break
                    
        return response
