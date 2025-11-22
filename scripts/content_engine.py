import random
import wikipedia
import re

def get_detailed_facts(animal):
    print(f"📚 Reading Full Wikipedia Page for: {animal}...")
    try:
        wikipedia.set_lang("en")
        # هات الصفحة كاملة مش الملخص
        try:
            page = wikipedia.page(animal, auto_suggest=False)
        except wikipedia.exceptions.DisambiguationError as e:
            page = wikipedia.page(e.options[0], auto_suggest=False)
        except:
            return []

        content = page.content
        # تنظيف النص
        content = re.sub(r'==.*?==+', '', content) # شيل العناوين
        content = re.sub(r'\n', ' ', content)      # شيل السطور الفاضية
        content = re.sub(r'\[.*?\]', '', content)  # شيل المصادر [1]
        
        # قسم النص لجمل طويلة
        sentences = content.split('. ')
        long_facts = []
        
        current_fact = ""
        for s in sentences:
            current_fact += s + ". "
            # الحقيقة الواحدة لازم تكون دسمة (أكتر من 150 حرف)
            if len(current_fact) > 150: 
                long_facts.append(current_fact.strip())
                current_fact = ""
                if len(long_facts) >= 10: break # كفاية 10 فقرات دسمة
        
        return long_facts
    except Exception as e:
        print(f"⚠️ Wikipedia Error: {e}")
        return []

def generate_script(animal_name, mode="short"):
    print(f"📝 Writing Script ({mode}) for: {animal_name}")
    
    hooks = [
        f"Prepare to be amazed by the top 10 facts about the {animal_name}.",
        f"Here is the ultimate guide to the {animal_name}. 10 things you didn't know.",
        f"Why is the {animal_name} so unique? Let's discover 10 reasons."
    ]
    hook = random.choice(hooks)
    
    if mode == "long":
        # --- DOCUMENTARY (3+ Minutes Goal) ---
        facts = get_detailed_facts(animal_name)
        
        # لو فشل يجيب حقائق طويلة، نملى بكلام عام عشان الوقت
        if len(facts) < 5:
            facts = [f"The {animal_name} is amazing and has many secrets in the wild."] * 10
            
        script_body = ""
        for i, fact in enumerate(facts):
            script_body += f"Fact number {i+1}: {fact} "
            # بنضيف وقفات بسيطة في النص
            script_body += "... " 

        outro = "Thank you for watching this documentary. Nature is truly fascinating. Which fact was your favorite? Tell us in the comments below. Don't forget to subscribe for more daily wildlife videos."
        
        script_text = f"{hook} ... {script_body} ... {outro}"
        
        title = f"10 Amazing Facts About The {animal_name} 🌍 (Full Documentary)"
        desc = f"Discover the secrets of the {animal_name} in this detailed documentary.\n\n#animals #wildlife #documentary #{animal_name.replace(' ', '')} #nature"
        tags = ["animals", "wildlife", "documentary", "10 facts", animal_name, "nature"]
        
    else:
        # --- SHORTS (Fast & Snappy) ---
        try:
            summary = wikipedia.summary(animal_name, sentences=3)
        except: summary = f"{animal_name} is cool."
        
        script_text = f"Did you know this about the {animal_name}? {summary} Subscribe for more!"
        title = f"{animal_name}: Mind Blowing Facts 🤯 #shorts"
        desc = f"Quick facts about {animal_name} #shorts"
        tags = ["shorts", "animals", "viral", animal_name]

    return {
        "title": title,
        "description": desc,
        "script_text": script_text,
        "tags": tags
    }
    
