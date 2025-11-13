import json
import random
from datetime import datetime, timedelta
from utils import load_json, save_json

class AnimalSelector:
    def __init__(self):
        self.used_animals_file = "data/used_animals.json"
        self.animal_db_file = "data/animal_database.json"
        self.used_animals = load_json(self.used_animals_file, [])
        self.animal_db = load_json(self.animal_db_file, self._get_default_animals())
        
    def _get_default_animals(self):
        """قائمة الحيوانات الافتراضية"""
        return {
            "mammals": ["Lion", "Elephant", "Tiger", "Giraffe", "Wolf", "Bear", "Kangaroo", "Panda"],
            "reptiles": ["Cobra", "Python", "Chameleon", "Komodo Dragon", "Alligator", "Turtle"],
            "birds": ["Eagle", "Parrot", "Penguin", "Owl", "Flamingo", "Peacock"],
            "fish": ["Shark", "Dolphin", "Clownfish", "Goldfish", "Piranha", "Manta Ray"],
            "insects": ["Butterfly", "Bee", "Ant", "Spider", "Dragonfly", "Ladybug"],
            "others": ["Horse", "Deer", "Donkey", "Zebra", "Fox", "Raccoon"]
        }
    
    def get_animal(self):
        """اختيار حيوان جديد مع تجنب التكرار"""
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
        
        selected_animal = random.choice(available_animals)
        
        # تسجيل الحيوان المستخدم
        self.used_animals.append({
            "animal": selected_animal,
            "date": datetime.now().isoformat()
        })
        save_json(self.used_animals_file, self.used_animals)
        
        return selected_animal
