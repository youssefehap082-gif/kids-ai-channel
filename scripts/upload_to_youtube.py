import os
from metadata import make_metadata                 # كودك لإنتاج القيم تلقائياً للـ SEO
from subtitles import add_subtitles                # ترجمة تلقائية متعددة اللغات
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_video(file_path, metadata, subtitles=[]):
    # ضبط اعتماد YouTube API قطعي حسب الأسرار الخاصة بك
    yt = build('youtube', 'v3', developerKey=os.environ['YT_CLIENT_ID'])
    body = {
        'snippet': {
            'title': metadata['title'],
            'description': metadata['description'],
            'tags': metadata['tags'],
            'categoryId': '15', # animals
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
    request = yt.videos().insert(
        part="snippet,status",
        body=body,
        media_body=file_path
    )
    response = request.execute()
    if subtitles:
        for lang, sub_path in subtitles.items():
            # ارفع ملف الترجمة كـ caption حسب لغة الترميز
            pass  # استخدم youtube.captions() لرفع الترجمة

def main():
    for file in os.listdir("outputs/long/"):
        if file.endswith(".mp4"):
            name = file.split(".")[0]
            md = make_metadata(name)
            subs = add_subtitles(name)
            upload_video(f"outputs/long/{file}", md, subtitles=subs)
    # كرر للشورتس إذا حبيت

if __name__ == "__main__":
    main()
