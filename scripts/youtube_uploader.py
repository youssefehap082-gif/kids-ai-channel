import os
import logging
import httplib2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

class RealYouTubeUploader:
    def __init__(self):
        self.youtube = self.get_authenticated_service()
    
    def get_authenticated_service(self):
        """الحصول على خدمة YouTube مصادقة"""
        try:
            # استخدام credentials من environment variables
            client_id = os.getenv('YT_CLIENT_ID')
            client_secret = os.getenv('YT_CLIENT_SECRET')
            refresh_token = os.getenv('YT_REFRESH_TOKEN')
            
            if not all([client_id, client_secret, refresh_token]):
                logging.error("❌ مفقود YouTube API credentials")
                return None
            
            # إنشاء credentials من refresh token
            from oauth2client.client import OAuth2Credentials
            credentials = OAuth2Credentials(
                None,  # No access token yet
                client_id,
                client_secret,
                refresh_token,
                None,  # No token expiry
                "https://accounts.google.com/o/oauth2/token",
                "YouTube Automation"
            )
            
            # بناء خدمة YouTube
            http = credentials.authorize(httplib2.Http())
            youtube_service = build("youtube", "v3", http=http)
            
            logging.info("✅ تم المصادقة مع YouTube API بنجاح")
            return youtube_service
            
        except Exception as e:
            logging.error(f"❌ فشل المصادقة مع YouTube API: {e}")
            return None

    def upload_video(self, video_path, content):
        """رفع فيديو فعلي على YouTube"""
        try:
            if self.youtube is None:
                logging.error("❌ خدمة YouTube غير متاحة")
                return None
            
            logging.info(f"🚀 بدء رفع الفيديو على YouTube: {content['title']}")
            
            # إعداد بيانات الفيديو
            body = {
                "snippet": {
                    "title": content["title"],
                    "description": content["description"],
                    "tags": content["tags"],
                    "categoryId": "22",  # Education
                    "defaultLanguage": "en",
                    "defaultAudioLanguage": "en"
                },
                "status": {
                    "privacyStatus": "public",  # يمكن تغييرها إلى "private" للاختبار
                    "selfDeclaredMadeForKids": False,
                    "embeddable": True,
                    "license": "youtube"
                }
            }
            
            # إنشاء طلب الرفع
            media = MediaFileUpload(
                video_path,
                chunksize=1024 * 1024,
                resumable=True,
                mimetype="video/mp4"
            )
            
            # إرسال طلب الرفع
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            # تنفيذ الرفع
            response = self.resumable_upload(request)
            
            if response and "id" in response:
                video_id = response["id"]
                logging.info(f"✅ تم رفع الفيديو بنجاح: {video_id}")
                logging.info(f"🔗 https://www.youtube.com/watch?v={video_id}")
                
                # إضافة الترجمة التلقائية
                self.add_automatic_captions(video_id, content)
                
                return video_id
            else:
                logging.error("❌ فشل رفع الفيديو - لا يوجد response")
                return None
                
        except Exception as e:
            logging.error(f"❌ خطأ في رفع الفيديو: {e}")
            return None

    def resumable_upload(self, request):
        """رفع قابل للاستئناف"""
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
                    logging.warning(f"⚠️ إعادة محاولة الرفع ({retry + 1}/{max_retries}): {e}")
                    retry += 1
                else:
                    logging.error(f"❌ فشل الرفع بعد {max_retries} محاولات: {e}")
                    break
                    
        return response

    def add_automatic_captions(self, video_id, content):
        """إضافة ترجمة تلقائية"""
        try:
            # تفعيل الترجمة التلقائية
            self.youtube.captions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "language": "en",
                        "name": f"Auto-captions for {content['animal']}",
                        "isDraft": False
                    }
                }
            ).execute()
            
            logging.info("✅ تم تفعيل الترجمة التلقائية")
            
        except Exception as e:
            logging.warning(f"⚠️ تعذر تفعيل الترجمة التلقائية: {e}")

    def upload_short(self, video_path, content):
        """رفع شورت على YouTube"""
        try:
            # نفس عملية الرفع العادية ولكن مع إشارة أن المحتوى قصير
            body = {
                "snippet": {
                    "title": content["title"],
                    "description": content["description"],
                    "tags": content["tags"],
                    "categoryId": "22",
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                },
                "contentDetails": {
                    "projection": "rectangular",
                    "hasCustomThumbnail": False
                }
            }
            
            media = MediaFileUpload(video_path, mimetype="video/mp4")
            
            request = self.youtube.videos().insert(
                part="snippet,status,contentDetails",
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            if "id" in response:
                video_id = response["id"]
                logging.info(f"✅ تم رفع الشورت بنجاح: {video_id}")
                return video_id
                
        except Exception as e:
            logging.error(f"❌ خطأ في رفع الشورت: {e}")
            return None
