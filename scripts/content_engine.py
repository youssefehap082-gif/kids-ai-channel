import random
import wikipedia
import re

def get_wiki_summary(animal):
    print(f"📚 Searching Wikipedia for: {animal}")
    try:
        wikipedia.set_lang("en")
        # نحاول نجيب ملخص
        try:
            summary = wikipedia.summary(animal, sentences=6)
        except wikipedia.exceptions.DisambiguationError as e:
            # لو الاسم متشابه، خد أول اقتراح
            summary = wikipedia.summary(e.options[0], sentences=6)
        except wikipedia.exceptions.PageError:
            # لو الصفحة مش موجودة
            return f"The {animal} is a fascinating creature. It lives in the wild and has unique behaviors."
            
        # تنظيف النص من الأقواس زي [1] [2]
        clean_summary = re.sub(r'\[.*?\]', '', summary)
        return clean_summary
    except Exception as e:
        print(f"⚠️ Wikipedia Error: {e}")
        return f"The {animal} is an amazing animal found in nature. Scientists are studying its unique lifestyle."

def generate_script(animal_name, mode="short"):
    print(f"📝 Writing Script ({mode}) for: {animal_name}")
    
    # 1. نجيب معلومات حقيقية
    wiki_text = get_wiki_summary(animal_name)
    
    # 2. جمل افتتاحية قوية (Hooks)
    hooks = [
        f"You won't believe this about the {animal_name}!",
        f"The {animal_name} is nature's ultimate machine.",
        f"Stop scrolling! Learn the truth about the {animal_name}.",
        f"Why is the {animal_name} so dangerous?",
        f"This is the most amazing fact about the {animal_name}."
    ]
    hook = random.choice(hooks)
    
    sentences = wiki_text.split('. ')
    # تنظيف الجمل الفارغة
    sentences = [s for s in sentences if len(s) > 10]

    if mode == "long":
        # --- DOCUMENTARY STYLE (فيديو طويل) ---
        # نختار أول 5-6 جمل دسمة
        body = ". ".join(sentences[:6])
        
        script_text = (
            f"{hook} Welcome to a deep dive into the world of the {animal_name}. "
            f"{body}. "
            f"These creatures are truly a marvel of evolution. Their survival instincts are unmatched in the wild. "
            f"Thank you for watching this documentary. Like and subscribe for more wildlife secrets."
        )
        
        title = f"The Life of {animal_name}: Full Documentary 🌍"
        desc = (
            f"Watch this full documentary about the {animal_name}. Real facts, amazing footage.\n\n"
            f"#animals #wildlife #documentary #{animal_name.replace(' ', '')} #nature"
        )
        tags = ["animals", "wildlife", "documentary", "nature", animal_name, "science", "education"]
        
    else:
        # --- SHORTS STYLE (فيديو قصير) ---
        fact1 = sentences[0] if len(sentences) > 0 else "It is amazing."
        fact2 = sentences[1] if len(sentences) > 1 else "It lives in the wild."
        
        script_text = f"{hook} Did you know? {fact1}. Also, {fact2}. Subscribe for more wild facts!"
        
        title = f"{animal_name}: The Shocking Truth 🤯 #shorts"
        desc = f"Crazy facts about {animal_name} #shorts #animals #wildlife"
        tags = ["shorts", "animals", "facts", "viral", animal_name]

    return {
        "title": title,
        "description": desc,
        "script_text": script_text,
        "tags": tags
    }
