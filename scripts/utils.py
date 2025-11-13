import json
import logging
import os
from datetime import datetime

def setup_logging():
    """إعداد نظام التسجيل"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/automation.log'),
            logging.StreamHandler()
        ]
    )

def load_json(file_path, default=None):
    """تحميل ملف JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def save_json(file_path, data):
    """حفظ بيانات لملف JSON"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_config():
    """تحميل الإعدادات"""
    return {
        "max_videos_per_day": 2,
        "max_shorts_per_day": 5,
        "video_duration": {"min": 180, "max": 600},  # 3-10 دقائق
        "short_duration": {"min": 15, "max": 60},    # 15-60 ثانية
        "target_languages": ["en", "es", "fr", "de", "ar"]
    }

def cleanup_temp_files():
    """تنظيف الملفات المؤقتة"""
    temp_dirs = ["outputs/temp", "logs"]
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
