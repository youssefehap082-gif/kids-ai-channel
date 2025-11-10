from moviepy.editor import TextClip, CompositeVideoClip
from googletrans import Translator
import os, tempfile

def generate_subtitles(text, lang="en"):
    lines = text.split('. ')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".srt", mode="w", encoding="utf-8") as f:
        start = 0
        for i, line in enumerate(lines):
            end = start + 4
            f.write(f"{i+1}\n00:00:{start:02d},000 --> 00:00:{end:02d},000\n{line.strip()}\n\n")
            start += 5
        return f.name

def add_text_overlay(video, text, lang="en"):
    try:
        clip = video
        lines = text.split('. ')
        y = 950
        txt_clips = []
        for line in lines:
            txt = TextClip(line.strip(), fontsize=45, color='white', font='Arial-Bold', bg_color='rgba(0,0,0,0.4)')
            txt = txt.set_position(("center", y)).set_duration(4).fadein(0.5).fadeout(0.5)
            y -= 60
            txt_clips.append(txt)
        return CompositeVideoClip([clip, *txt_clips])
    except Exception as e:
        print(f"⚠️ Error adding overlay: {e}")
        return video

def translate_text(text, languages=None):
    if languages is None:
        languages = ["es", "de", "fr", "pt"]  # Spanish, German, French, Portuguese
    translator = Translator()
    translations = {}
    for lang in languages:
        try:
            translations[lang] = translator.translate(text, dest=lang).text
        except Exception as e:
            print(f"⚠️ Translation failed for {lang}: {e}")
    return translations
