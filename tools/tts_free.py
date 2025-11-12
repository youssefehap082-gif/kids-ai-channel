from gtts import gTTS

def synthesize_free_tts(text, out_path="output.mp3", lang="en", slow=False):
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(out_path)
    return out_path
