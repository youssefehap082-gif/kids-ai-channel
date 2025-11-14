import os
import json
import logging
from utils import load_json

class ContentGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    def generate_animal_content(self, animal, for_short=False):
        """إنشاء محتوى متكامل عن الحيوان"""
        try:
            # الحصول على حقائق عن الحيوان
            facts = self._get_animal_facts(animal)
            
            # إنشاء السيناريو
            if for_short:
                script = self._generate_short_script(animal, facts)
            else:
                script = self._generate_long_script(animal, facts)
            
            # إنشاء محتوى SEO محسن
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
            
            logging.info(f"✅ تم إنشاء محتوى لـ {animal}")
            return content
            
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء المحتوى: {e}")
            return self._get_fallback_content(animal, for_short)
    
    def _get_animal_facts(self, animal):
        """الحصول على 10 حقائق مميزة عن الحيوان"""
        try:
            if self.openai_api_key:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "user",
                        "content": f"""Generate 10 amazing and educational facts about {animal} that will surprise viewers.
                        Make them engaging, viral-worthy, and perfect for YouTube.
                        Return as JSON array of strings."""
                    }],
                    temperature=0.8
                )
                
                facts_text = response.choices[0].message.content
                facts = json.loads(facts_text)
                return facts[:10]
                
        except Exception as e:
            logging.warning(f"OpenAI غير متوفر: {e}")
        
        # حقائق افتراضية
        return self._get_default_facts(animal)
    
    def _generate_long_script(self, animal, facts):
        """إنشاء سيناريو للفيديو الطويل"""
        script = f"Welcome to Animal Facts Daily! Today, we explore the incredible world of {animal}s. "
        script += "Get ready to be amazed by these fascinating facts: "
        
        for i, fact in enumerate(facts, 1):
            script += f"Fact {i}: {fact}. "
        
        script += "Which fact surprised you the most? Let us know in the comments! "
        script += "If you enjoyed this journey into the animal kingdom, don't forget to subscribe and hit the bell for more amazing wildlife content every single day!"
        
        return script
    
    def _generate_short_script(self, animal, facts):
        """إنشاء سيناريو للشورت (مختصر)"""
        return f"Discover {animal}s! {facts[0]} {facts[1]} Follow for daily animal facts! 🐾"
    
    def _generate_seo_content(self, animal, for_short):
        """إنشاء محتوى SEO محسن"""
        try:
            if self.openai_api_key:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                
                video_type = "YouTube Short" if for_short else "YouTube video"
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "user",
                        "content": f"""Create viral YouTube SEO content for a {video_type} about {animal}.
                        Make it engaging, clickable, and optimized for maximum views.
                        Return JSON: {{"title": "...", "description": "...", "tags": ["..."]}}
                        For shorts, include #shorts in title."""
                    }],
                    temperature=0.9
                )
                
                content = json.loads(response.choices[0].message.content)
                return content["title"], content["description"], content["tags"]
                
        except Exception as e:
            logging.warning(f"OpenAI SEO غير متوفر: {e}")
        
        return self._get_fallback_seo(animal, for_short)
    
    def _get_default_facts(self, animal):
        """حقائق افتراضية"""
        return [
            f"{animal}s have incredible adaptations that help them survive in their environments",
            f"They play vital roles in maintaining ecosystem balance",
            f"Their unique behaviors and social structures are fascinating to study",
            f"{animal}s have evolved over millions of years to perfection",
            f"Conservation efforts are crucial for protecting these amazing creatures",
            f"Their physical characteristics are perfectly suited to their lifestyle",
            f"{animal}s communicate in complex ways we're still understanding",
            f"Their diet and hunting strategies are remarkably efficient",
            f"Baby {animal}s have adorable and interesting development stages",
            f"These animals face important challenges in the modern world"
        ]
    
    def _get_fallback_seo(self, animal, for_short):
        """محتوى SEO افتراضي"""
        if for_short:
            title = f"🤯 {animal} Facts That Will Blow Your Mind! #shorts #animals"
        else:
            title = f"10 Incredible {animal} Facts You Won't Believe! | Wildlife Documentary"
        
        description = f"Discover the amazing world of {animal}s! In this video, we explore fascinating facts about {animal} behavior, habitat, and unique characteristics that will surprise you.\n\n"
        description += "🔔 Subscribe for daily animal facts\n"
        description += "👍 Like this video if you learned something new!\n"
        description += "💬 Comment which fact surprised you most!\n\n"
        description += "📱 Follow us for more wildlife content!\n\n"
        description += f"#{animal} #animals #wildlife #nature #education #animalfacts"
        
        tags = [
            animal, f"{animal} facts", "animals", "wildlife", "nature", 
            "animal facts", "wildlife documentary", "nature documentary",
            "educational video", "animal education", "wildlife education",
            "amazing animals", "animal behavior", "wildlife facts"
        ]
        
        return title, description, tags
    
    def _get_fallback_content(self, animal, for_short):
        """محتوى احتياطي كامل"""
        facts = self._get_default_facts(animal)
        title, description, tags = self._get_fallback_seo(animal, for_short)
        script = self._generate_short_script(animal, facts) if for_short else self._generate_long_script(animal, facts)
        
        return {
            "animal": animal,
            "facts": facts,
            "script": script,
            "title": title,
            "description": description,
            "tags": tags,
            "is_short": for_short
        }
