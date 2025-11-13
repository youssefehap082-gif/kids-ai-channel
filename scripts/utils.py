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
    logging.info("🚀 بدء نظام أتمتة YouTube")

def load_config():
    """تحميل الإعدادات"""
    return {
        "max_videos_per_day": 2,
        "max_shorts_per_day": 5,
        "video_duration": 30,
        "short_duration": 15
    }
