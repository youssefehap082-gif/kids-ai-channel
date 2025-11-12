import os, random, requests, datetime, time, re
from gtts import gTTS
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip, TextClip
from youtube import upload_video

# 🦁 قائمة الحيوانات والمعلومات
animals = {
    "Lion": "The lion is the king of the jungle, powerful and majestic.",
    "Elephant": "Elephants are intelligent and emotional giants of the wild.",
    "Dolphin": "Dolphins are friendly, smart, and communicate using sound.",
    "Tiger": "Tigers are solitary hunters with unmatched strength.",
    "Wolf": "Wolves are pack animals known for their loyalty and teamwork.",
    "Panda": "Pandas are calm and peaceful bamboo eaters.",
    "Eagle": "Eagles can spot prey from miles away with their sharp vision.",
    "Giraffe": "Giraffes are the tallest animals on Earth with long elegant necks."
}

animal, fact = random.choice(list(animals.items()))
print(f"🎬 Creating long video for {animal}")

# 🎤 توليد التعليق الصوتي (ذكر / أنثى)
voice_gender = random.choice(["male", "female"])
tts_text = f"Here are some amazing facts about the {animal}. {fact}"
tts = gTTS(text=tts_text, lang="en", slow=False)
tts.save("voice.mp3")

# 🖼️ تحميل صور من Pexels
PEXELS_API = os.getenv("PEXELS_API_KEY")
headers = {"Authorization": PEXELS_API}
res = requests.get(f"https://api.pexels.com/v1/search?query={animal}&per_page=8", headers=headers).json()
images = [photo["src"]["medium"] for photo in res["photos"] if "src" in photo]

os.makedirs("frames", exist_ok=True)
for i, url in enumerate(images):
    img_data = requests.get(url).content
    with open(f"frames/frame{i}.jpg", "wb") as f:
        f.write(img_data)

# 🎥 إنشاء الفيديو
clip = ImageSequenceClip(["frames/" + f for f in os.listdir("frames")], fps=1)
audio = AudioFileClip("voice.mp3")
duration = audio.duration
subtitle = TextClip(fact, fontsize=36, color='white', bg_color='black', size=(720, 120)).set_duration(duration).set_position(("center", "bottom"))
final = CompositeVideoClip([clip.set_audio(audio), subtitle]).set_duration(duration)
file_name = f"{animal.lower()}_facts.mp4"
final.write_videofile(file_name, fps=24)

# 💬 توليد ملف ترجمة SRT
def generate_srt(text, duration):
    lines = re.findall('.{1,40}(?:\s+|$)', text)
    part_duration = duration / len(lines)
    srt = ""
    for i, line in enumerate(lines):
        start = str(datetime.timedelta(seconds=int(i * part_duration)))
        end = str(datetime.timedelta(seconds=int((i + 1) * part_duration)))
        srt += f"{i+1}\n0{start},000 --> 0{end},000\n{line.strip()}\n\n"
    return srt

srt_content = generate_srt(tts_text, duration)
with open("subtitles.srt", "w", encoding="utf-8") as f:
    f.write(srt_content)

# 🧠 تحسين الـ SEO
title = f"Amazing Facts About {animal} 🐾 | AI Wildlife Documentary"
description = f"Discover incredible facts about {animal}! AI voice, subtitles, and HD visuals.\n\n#AI #Wildlife #Nature #Facts #Animals"
tags = [animal.lower(), "AI", "wildlife", "documentary", "nature", "facts"]

# ⏰ أفضل مواعيد نشر (جمهور أجنبي)
hour = datetime.datetime.utcnow().hour
if 16 <= hour <= 23:
    schedule_time = "Prime Time (US)"
else:
    schedule_time = "Morning (Europe)"
print(f"🕓 Posting during: {schedule_time}")

# 🚀 رفع الفيديو
for attempt in range(3):
    try:
        print(f"🚀 Attempt {attempt+1} upload...")
        upload_video(file_name, title, description, tags)
        print("✅ Uploaded successfully!")
        break
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        time.sleep(600)
