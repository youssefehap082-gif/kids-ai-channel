import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

class YouTubeUploader:
    def __init__(self):
        self.channel_id = os.getenv("YT_CHANNEL_ID")
        self.credentials = self._get_credentials()
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

    def _get_credentials(self):
        """الحصول على بيانات الاعتماد من الـ secrets"""
        # استخدام refresh token للحصول على access token جديد
        # هذا مثال مبسط - قد تحتاج إلى تعديله حسب طريقة حصولك على الـ refresh token
        credentials = Credentials(
            token=None,
            refresh_token=os.getenv("YT_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("YT_CLIENT_ID"),
            client_secret=os.getenv("YT_CLIENT_SECRET")
        )
        return credentials

    def upload_video(self, video_path, content):
        """رفع فيديو حقيقي إلى اليوتيوب"""
        try:
            body = {
                'snippet': {
                    'title': content['title'],
                    'description': content['description'],
                    'tags': content['tags'],
                    'categoryId': '22'  # Education
                },
                'status': {
                    'privacyStatus': 'public',  # أو 'private' أو 'unlisted'
                    'selfDeclaredMadeForKids': False
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = self._execute_upload(request)
            if response:
                video_id = response['id']
                logging.info(f"تم رفع الفيديو بنجاح: {video_id}")
                return video_id

        except Exception as e:
            logging.error(f"خطأ في رفع الفيديو: {e}")
            return None

    def _execute_upload(self, request):
        """تنفيذ عملية الرفع مع التعامل مع الأخطاء"""
        response = None
        retry = 0
        while response is None and retry < 3:
            try:
                status, response = request.next_chunk()
                if response is not None:
                    return response
            except Exception as e:
                logging.error(f"خطأ في رفع جزء من الفيديو: {e}")
                retry += 1
        return None
