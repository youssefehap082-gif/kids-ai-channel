import openai
import os
import json
from utils import load_json, save_json

class ContentGenerator:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.performance_file = "data/performance_data.json"
        
    def generate_animal_content(self, animal, for_short=False):
        """إنشاء محتوى عن الحيوان"""
        try:
            # الحصول على حقائق عن الحيوان
            facts = self._get_animal_facts(animal)
            
            # إنشاء السيناريو
            if for_short:
                script = self._generate_short_script(animal, facts)
            else:
                script = self._generate_long_script(animal, facts)
            
            # إنشاء العناوين والوصف
            title, description, tags = self._generate_seo_content(animal, for_short)
            
            return {
                "animal": animal,
                "facts": facts,
                "script": script,
                "title": title,
                "description": description,
                "tags": tags,
                "is_short": for_short
            }
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return self._get_fallback_content(animal, for_short)
    
    def _get_animal_facts(self, animal):
        """الحصول على 10 حقائق عن الحيوان باستخدام الذكاء الاصطناعي"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": f"Generate 10 interesting and educational facts about {animal}. Make them engaging for YouTube audience. Return as JSON array of strings."
                }]
            )
            
            facts_text = response.choices[0].message.content
            facts = json.loads(facts_text)
            return facts[:10]  # تأكد من 10 حقائق فقط
            
        except Exception as e:
            print(f"Error getting facts from AI: {e}")
            return self._get_default_facts(animal)
    
    def _generate_long_script(self, animal, facts):
        """إنشاء سيناريو للفيديو الطويل"""
        script_intro = f"Welcome to our channel! Today we're exploring the fascinating world of {animal}. "
        script_body = "Here are 10 amazing facts you probably didn't know: "
        
        for i, fact in enumerate(facts, 1):
            script_body += f"{i}. {fact} "
        
        script_outro = "Which fact surprised you the most? Let us know in the comments! Don't forget to subscribe and hit the bell for more amazing animal content!"
        
        return script_intro + script_body + script_outro
    
    def _generate_short_script(self, animal, facts):
        """إنشاء سيناريو للشورت (مختصر)"""
        return f"Amazing {animal} facts! {facts[0]} {facts[1]} Follow for more animal content! 🐾"
    
    def _generate_seo_content(self, animal, for_short):
        """إنشاء محتوى محسن لمحركات البحث"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": f"""Generate SEO-optimized YouTube content for a video about {animal}.
                    {'This is a YouTube Short' if for_short else 'This is a long form video'}.
                    Return JSON with: title, description, tags (array).
                    Make it engaging and viral."""
                }]
            )
            
            content = json.loads(response.choices[0].message.content)
            return content["title"], content["description"], content["tags"]
            
        except Exception as e:
            return self._get_fallback_seo(animal, for_short)
    
    def _get_default_facts(self, animal):
        """حقائق افتراضية إذا فشل الذكاء الاصطناعي"""
        return [
            f"The {animal} is a fascinating creature",
            f"{animal}s have unique adaptations",
            f"They play important roles in their ecosystems",
            f"{animal}s have diverse habitats",
            f"Their diet varies widely",
            f"They have interesting social behaviors",
            f"{animal}s face various conservation challenges",
            f"They have remarkable physical characteristics",
            f"Their reproduction methods are fascinating",
            f"{animal}s have existed for millions of years"
        ]
    
    def _get_fallback_seo(self, animal, for_short):
        """محتوى SEO افتراضي"""
        if for_short:
            title = f"Amazing {animal} Facts! 🐾 #shorts"
        else:
            title = f"10 Incredible Facts About {animal}s You Won't Believe!"
        
        description = f"Learn amazing facts about {animal}s in this educational video. "
        description += "Don't forget to subscribe and hit the bell for more animal content!\n\n"
        description += "#animals #wildlife #education #nature"
        
        tags = [animal, "animals", "wildlife", "facts", "education", "nature"]
        
        return title, description, tags
