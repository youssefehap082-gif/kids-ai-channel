# scripts/animal_selector.py

import json
import random
from pathlib import Path

DATA_DIR = Path("data")
USED_FILE = DATA_DIR / "used_animals.json"

# ======================================================
# 1) قائمة الحيوانات الأساسية (حسب طلبك)
# ======================================================
ANIMAL_LIST = [
    "lion", "tiger", "elephant", "giraffe", "zebra", "hippopotamus",
    "rhinoceros", "cheetah", "leopard", "bear", "wolf", "fox",
    "kangaroo", "koala", "panda", "chimpanzee", "gorilla", "orangutan",
    "hyena", "buffalo", "camel", "ostrich", "emu", "eagle", "falcon",
    "albatross", "penguin", "seal", "dolphin", "whale", "shark",
    "octopus", "jellyfish", "crocodile", "alligator", "cobra",
    "python", "king cobra", "rattlesnake", "frog", "toad", "salamander",
    "butterfly", "bee", "ant", "grasshopper", "cricket", "tarantula",
    "scorpion", "praying mantis"
]

# ======================================================
# 2) تحميل سجل الحيوانات المستخدمة
# ======================================================
def load_used():
    if USED_FILE.exists():
        try:
            return json.loads(USED_FILE.read_text())
        except:
            return []
    return []

# ======================================================
# 3) حفظ السجل
# ======================================================
def save_used(lst):
    USED_FILE.write_text(json.dumps(lst, indent=2))

# ======================================================
# 4) اختيار الحيوانات لليوم
# ======================================================
def pick_animals(num_needed: int):
    """
    Picks N unique animals without repeating previous runs.
    When exhausted, automatically resets the used list.
    """
    used = load_used()
    available = [a for a in ANIMAL_LIST if a not in used]

    # لو خلصوا — نصفر القائمة
    if len(available) < num_needed:
        used = []
        save_used(used)
        available = ANIMAL_LIST.copy()

    picked = random.sample(available, num_needed)

    # تحديث المستخدم
    new_used = used + picked
    save_used(new_used)

    return picked
