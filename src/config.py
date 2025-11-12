# المسار: src/config.py

import os

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# AI Voice
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
# IDs لأصوات مختلفة (هتحتاج تجيبها من حسابك في ElevenLabs)
VOICE_ID_MALE = "pNInz6obpgDQGcFmaJgB"  # مثال: "Adam"
VOICE_ID_FEMALE = "EXAVITQu4vr4wKLbuV3C" # مثال: "Rachel"

# AI Models
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
# موديل Whisper على Replicate (لعمل الترجمة)
WHISPER_MODEL = "openai/whisper:4d5079b61D02ced06e6a96a8920638df9fC2bAFD1de55f27BC206f08D"

# Stock Videos
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
# (Storyblocks, Coverr, etc. هنستخدم requests معاهم)

# YouTube
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")

# Paths
STATE_FILE = "used_animals.txt"
ASSETS_DIR = "assets" # فولدر مؤقت للملفات
