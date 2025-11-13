import json
import random
from datetime import datetime, timedelta
import logging

try:
    from utils import load_json, save_json
except ImportError:
    # نسخة بديلة إذا فشل الاستيراد
    import json
    import os
    
    def load_json(file_path, default=None):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return default if default is not None else {}
    
    def save_json(file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

class AnimalSelector:
    def __init__(self):
        self.used_animals_file = "data/used_animals.json"
        self.animal_db_file = "data/animal_database.json"
        self.used_animals = load_json(self.used_animals_file, [])
        self.animal_db = load_json(self.animal_db_file, self._get_default_animals())
        logging.info("تم تهيئة AnimalSelector")
        
    def _get_default_animals(self):
        """قائمة الحيوانات الافتراضية"""
        return {
            "mammals": ["Lion", "Elephant", "Tiger", "Giraffe", "Wolf", "Bear", "Kangaroo", "Panda", "Zebra", "Fox"],
            "reptiles": ["Cobra", "Python", "Chameleon", "Komodo Dragon", "Alligator", "Turtle", "Crocodile", "Iguana"],
            "birds": ["Eagle", "Parrot", "Penguin", "Owl", "Flamingo", "Peacock", "Hawk", "Swan"],
            "fish": ["Shark", "Dolphin", "Clownfish", "Goldfish", "Piranha", "Manta Ray", "Whale", "Octopus"],
            "insects": ["Butterfly", "Bee", "Ant", "Spider", "Dragonfly", "Ladybug", "Grasshopper", "Beetle"],
            "others": ["Horse", "Deer", "Donkey", "Rabbit", "Raccoon", "Hedgehog", "Squirrel", "Bat"]
        }
    
    def get_animal(self):
        """اختيار حيوان جديد مع تجنب التكرار"""
        try:
            # تنظيف الحيوانات المستخدمة قبل أكثر من أسبوع
            week_ago = datetime.now() - timedelta(days=7)
            self.used_animals = [u for u in self.used_animals 
                               if datetime.fromisoformat(u['date']) > week_ago]
            
            # جميع الحيوانات المتاحة
            all_animals = []
            for category, animals in self.animal_db.items():
                all_animals.extend(animals)
            
            # استبعاد المستخدمة حديثاً
            used_recently = [u['animal'] for u in self.used_animals]
            available_animals = [a for a in all_animals if a not in used_recently]
            
            if not available_animals:
                # إذا لم يوجد حيوانات جديدة، نعيد استخدام القديمة
                available_animals = all_animals
                logging.info("إعادة استخدام الحيوانات القديمة بسبب عدم توفر جديدة")
            
            selected_animal = random.choice(available_animals)
            
            # تسجيل الحيوان المستخدم
            self.used_animals.append({
                "animal": selected_animal,
                "date": datetime.now().isoformat(),
                "category": self._find_animal_category(selected_animal)
            })
            save_json(self.used_animals_file, self.used_animals)
            
            logging.info(f"تم اختيار الحيوان: {selected_animal}")
            return selected_animal
            
        except Exception as e:
            logging.error(f"خطأ في اختيار الحيوان: {e}")
            # عودة إلى قائمة افتراضية في حالة الخطأ
            default_animals = ["Lion", "Elephant", "Tiger", "Giraffe", "Dolphin"]
            return random.choice(default_animals)
    
    def _find_animal_category(self, animal):
        """إيجاد فئة الحيوان"""
        for category, animals in self.animal_db.items():
            if animal in animals:
                return category
        return "unknown"
