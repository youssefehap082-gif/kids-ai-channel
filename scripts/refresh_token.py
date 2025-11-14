#!/usr/bin/env python3
import os
import json
import requests
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

def refresh_youtube_token():
    """تجديد YouTube API Token"""
    print("🔄 بدء تجديد YouTube Token...")
    
    # بيانات الـ OAuth 2.0 من Google Cloud Console
    client_id = os.getenv('YT_CLIENT_ID')
    client_secret = os.getenv('YT_CLIENT_SECRET')
    refresh_token = os.getenv('YT_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ missing environment variables")
        return None
    
    try:
        # تجديد الـ Token
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=data)
        result = response.json()
        
        if 'access_token' in result:
            new_access_token = result['access_token']
            print(f"✅ تم تجديد الـ Token بنجاح!")
            print(f"🆕 الـ Access Token الجديد: {new_access_token[:20]}...")
            return new_access_token
        else:
            print(f"❌ فشل تجديد الـ Token: {result}")
            return None
            
    except Exception as e:
        print(f"❌ خطأ في تجديد الـ Token: {e}")
        return None

def get_new_refresh_token():
    """الحصول على Refresh Token جديد (إذا انتهى)"""
    print("🚀 بدء عملية الحصول على Refresh Token جديد...")
    
    client_config = {
        "web": {
            "client_id": os.getenv('YT_CLIENT_ID'),
            "client_secret": os.getenv('YT_CLIENT_SECRET'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080"]
        }
    }
    
    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/youtube.upload'],
            redirect_uri='http://localhost:8080'
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        
        print(f"🌐 الرجاء زيارة هذا الرابط في المتصفح:")
        print(auth_url)
        print("\n➡️ بعد الموافقة، ستحصل على رمز. الصق الرمز هنا:")
        
        auth_code = input("أدخل رمز المصادقة: ").strip()
        
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        print(f"✅ تم الحصول على Tokens جديدة!")
        print(f"🆕 Access Token: {credentials.token[:20]}...")
        print(f"🆕 Refresh Token: {credentials.refresh_token}")
        
        return credentials.refresh_token
        
    except Exception as e:
        print(f"❌ خطأ في الحصول على Token جديد: {e}")
        return None

if __name__ == "__main__":
    print("🔧 أداة تجديد YouTube Tokens")
    print("1. تجديد Access Token الحالي")
    print("2. الحصول على Refresh Token جديد")
    
    choice = input("اختر الخيار (1 أو 2): ").strip()
    
    if choice == "1":
        token = refresh_youtube_token()
        if token:
            print("🎉 تم تجديد الـ Token بنجاح!")
    elif choice == "2":
        new_refresh_token = get_new_refresh_token()
        if new_refresh_token:
            print(f"🎉 الـ Refresh Token الجديد: {new_refresh_token}")
            print("⚠️  قم بنسخ هذا الـ Token وتحديثه في GitHub Secrets")
    else:
        print("❌ اختيار غير صحيح")
