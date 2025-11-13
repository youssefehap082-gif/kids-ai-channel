import os
import json
import logging

try:
    from utils import load_json, save_json
except ImportError:
    # استيراد بديل
    import json
    import os

class ContentGenerator:
    def __init__(self):
        self.performance_file = "data/performance_data.json"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        logging.info("تم تهيئة ContentGenerator")
        
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
            
            content = {
                "animal": animal,
                "facts": facts,
                "script": script,
                "title": title,
                "description": description,
                "tags": tags,
                "is_short": for_short
            }
            
            logging.info(f"تم إنشاء محتوى لـ {animal}")
            return content
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء المحتوى: {e}")
            return self._get_fallback_content(animal, for_short)
    
    def _get_animal_facts(self, animal):
        """الحصول على 10 حقائق عن الحيوان"""
        try:
            # إذا كان هناك مفتاح OpenAI، استخدمه
            if self.openai_api_key:
                try:
                    import openai
                    openai_client = openai.OpenAI(api_key=self.openai_api_key)
                    
                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{
                            "role": "user",
                            "content": f"Generate 10 interesting facts about {animal}. Return as JSON array."
                        }]
                    )
                    
                    facts_text = response.choices[0].message.content
                    facts = json.loads(facts_text)
                    return facts[:10]
                    
                except Exception as e:
                    logging.warning(f"OpenAI failed, using default facts: {e}")
            
            # استخدام الحقائق الافتراضية
            return self._get_default_facts(animal)
            
        except Exception as e:
            logging.error(f"Error getting facts: {e}")
            return self._get_default_facts(animal)
    
    def _generate_long_script(self, animal, facts):
        """إنشاء سيناريو للفيديو الطويل"""
        script_intro = f"Welcome to our channel! Today we're exploring the fascinating world of {animal}. "
        script_body = "Here are 10 amazing facts you probably didn't know: "
        
        for i, fact in enumerate(facts, 1):
            script_body += f"{i}. {fact}. "
        
        script_outro = "Which fact surprised you the most? Let us know in the comments! Don't forget to subscribe and hit the bell for more amazing animal content!"
        
        return script_intro + script_body + script_outro
    
    def _generate_short_script(self, animal, facts):
        """إنشاء سيناريو للشورت (مختصر)"""
        return f"Amazing {animal} facts! {facts[0]} {facts[1]} Follow for more animal content! 🐾"
    
    def _generate_seo_content(self, animal, for_short):
        """إنشاء محتوى محسن لمحركات البحث"""
        try:
            if self.openai_api_key:
                try:
                    import openai
                    openai_client = openai.OpenAI(api_key=self.openai_api_key)
                    
                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{
                            "role": "user",
                            "content": f"""Create YouTube SEO content for {animal}.
                            {'Short video' if for_short else 'Long video'}.
                            Return JSON: {{"title": "...", "description": "...", "tags": ["..."]}}"""
                        }]
                    )
                    
                    content = json.loads(response.choices[0].message.content)
                    return content["title"], content["description"], content["tags"]
                    
                except Exception as e:
                    logging.warning(f"OpenAI SEO failed: {e}")
            
            return self._get_fallback_seo(animal, for_short)
            
        except Exception as e:
            logging.error(f"SEO content error: {e}")
            return self._get_fallback_seo(animal, for_short)
    
    def _get_default_facts(self, animal):
        """حقائق افتراضية إذا فشل الذكاء الاصطناعي"""
        return [
            f"The {animal} is a fascinating creature with unique characteristics",
            f"{animal}s play important roles in their ecosystems",
            f"They have adapted to survive in their specific environments",
            f"The diet of {animal}s varies depending on species and habitat",
            f"{animal}s have interesting social behaviors and communication methods",
            f"These animals face various conservation challenges worldwide",
            f"The physical characteristics of {animal}s are remarkable",
            f"Their reproduction and life cycle are fascinating to study",
            f"{animal}s have existed on Earth for millions of years",
            f"These creatures are important to maintaining biodiversity"
        ]
    
    def _get_fallback_content(self, animal, for_short):
        """محتوى احتياطي كامل"""
        facts = self._get_default_facts(animal)
        title, description, tags = self._get_fallback_seo(animal, for_short)
        script = self._generate_long_script(animal, facts) if not for_short else self._generate_short_script(animal, facts)
        
        return {
            "animal": animal,
            "facts": facts,
            "script": script,
            "title": title,
            "description": description,
            "tags": tags,
            "is_short": for_short
        }
    
    def _get_fallback_seo(self, animal, for_short):
        """محتوى SEO افتراضي"""
        if for_short:
            title = f"Amazing {animal} Facts! 🐾 #shorts"
        else:
            title = f"10 Incredible Facts About {animal}s You Won't Believe!"
        
        description = f"Learn amazing facts about {animal}s in this educational video. "
        description += f"Discover fascinating information about {animal} behavior, habitat, and characteristics. "
        description += "Don't forget to subscribe and hit the bell for more animal content!\n\n"
        description += f"#{animal} #animals #wildlife #education #nature #facts"
        
        tags = [animal, "animals", "wildlife", "facts", "education", "nature", "animal facts", "wildlife education"]
        
        return title, description, tags
