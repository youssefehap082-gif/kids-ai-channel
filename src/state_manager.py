# المسار: src/state_manager.py

import os
from src.config import STATE_FILE

# أسبوع = 7 أيام * 7 فيديوهات/يوم = 49. هنخليها 50 للاحتياط
MAX_HISTORY = 50 

def get_used_animals() -> list:
    """يقرأ قائمة الحيوانات المستخدمة مؤخرًا"""
    if not os.path.exists(STATE_FILE):
        return []
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        animals = [line.strip() for line in f.readlines()]
    return animals

def add_used_animals(new_animals: list):
    """يضيف الحيوانات الجديدة للقائمة ويحفظها"""
    print(f"Adding to state: {new_animals}")
    current_animals = get_used_animals()
    # بنضيف الجديد في الأول
    updated_list = new_animals + current_animals
    
    # بنشيل التكرار (مع الحفاظ على الترتيب)
    unique_list = list(dict.fromkeys(updated_list))
    
    # بنحافظ على آخر 50 حيوان بس
    final_list = unique_list[:MAX_HISTORY]
    
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_list))
