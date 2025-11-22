import random
import wikipedia
import re

def get_10_facts(animal):
    print(f"📚 Researching 10 Facts for: {animal}")
    try:
        wikipedia.set_lang("en")
        # بنجيب ملخص كبير شوية عشان ننقي منه
        try:
            # بنطلب 20 جملة عشان نضمن نلاقي 10 كويسين
            full_summary = wikipedia.summary(animal, sentences=20)
        except wikipedia.exceptions.DisambiguationError as e:
            full_summary = wikipedia.summary(e.options[0], sentences=20)
        except wikipedia.exceptions.PageError:
            return [f"{animal} is amazing."] * 10
            
        # تنظيف النص وتقسيمه لجمل
        clean_text = re.sub(r'\[.*?\]', '', full_summary)
        sentences = clean_text.split('. ')
        
        # فلترة الجمل القصيرة أوي (أقل من 20 حرف) عشان الجودة
        valid_sentences = [s.strip() for s in sentences if len(s) > 20]
        
        # لو لقينا أقل من 10، نكرر أو نكتفي بالموجود
        if len(valid_sentences) < 10:
            return valid_sentences
            
        # نختار أول 10 جمل (غالباً هم الأهم)
        return valid_sentences[:10]
        
    except Exception as e:
        print(f"⚠️ Wikipedia Error: {e}")
        return [f"{animal} is a unique creature found in nature."] * 10

def generate_script(animal_name, mode="short"):
    print(f"📝 Writing Script ({mode}) for: {animal_name}")
    
    # Hooks
    hooks = [
        f"Get ready to learn the top 10 facts about the {animal_name}!",
        f"Here are 10 things you didn't know about the {animal_name}.",
        f"Why is the {animal_name} so special? Here are 10 reasons.",
        f"The ultimate guide to the {animal_name} in 10 facts."
    ]
    hook = random.choice(hooks)
    
    # جلب الحقائق
    facts_list = get_10_facts(animal_name)
    
    if mode == "long":
        # --- DOCUMENTARY STYLE (10 FACTS LIST) ---
        # بناء السكريبت كنقاط محددة
        script_body = ""
        for i, fact in enumerate(facts_list):
            # بنضيف رقم الحقيقة عشان المشاهد يتابع
            script_body += f"Fact number {i+1}: {fact}. "
        
        script_text = (
            f"{hook} Welcome to Wild Facts Hub. "
            f"{script_body} "
            f"Which fact surprised you the most? Let us know in the comments. "
            f"Thanks for watching, don't forget to like and subscribe."
        )
        
        title = f"10 Amazing Facts About The {animal_name} 🌍"
        desc = (
            f"Top 10 facts about the {animal_name}. Discover the secrets of nature.\n\n"
            f"#animals #wildlife #documentary #{animal_name.replace(' ', '')} #nature #10facts"
        )
        tags = ["animals", "wildlife", "documentary", "10 facts", animal_name, "education"]
        
    else:
        # --- SHORTS STYLE (3 FACTS ONLY) ---
        # الشورتس مايستحملش 10، هناخد أهم 3 بس
        short_facts = facts_list[:3]
        script_text = f"Did you know this about the {animal_name}? {short_facts[0]}. {short_facts[1]}. And finally, {short_facts[2]}. Subscribe for more!"
        
        title = f"{animal_name}: 3 Shocking Facts 🤯 #shorts"
        desc = f"Crazy facts about {animal_name} #shorts #animals #wildlife"
        tags = ["shorts", "animals", "facts", "viral", animal_name]

    return {
        "title": title,
        "description": desc,
        "script_text": script_text,
        "tags": tags
    }
