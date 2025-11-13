import json
import logging
import os
from datetime import datetime

def setup_logging():
    """إعداد نظام التسجيل"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/automation.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.info("=== بدء النظام ===")

def load_json(file_path, default=None):
    """تحميل ملف JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Could not load {file_path}: {e}")
        return default if default is not None else {}

def save_json(file_path, data):
    """حفظ بيانات لملف JSON"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"تم حفظ البيانات في: {file_path}")
    except Exception as e:
        logging.error(f"خطأ في حفظ {file_path}: {e}")

def load_config():
    """تحميل الإعدادات"""
    return {
        "max_videos_per_day": 2,
        "max_shorts_per_day": 5,
        "video_duration": {"min": 180, "max": 600},
        "short_duration": {"min": 15, "max": 60},
        "target_languages": ["en", "es", "fr", "de", "ar"],
        "test_mode": True
    }
