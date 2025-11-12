# المسار: src/config.py

import os

# AI (Free)
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# HF Model IDs
HF_LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2" # للكتابة
HF_TTS_MODEL = "facebook/mms-tts-eng" # للصوت

# Stock Videos
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# YouTube
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")

# Paths
STATE_FILE = "used_animals.txt"
ASSETS_DIR = "assets"
