# scripts/fetch_wikipedia.py

import wikipedia
import re

# إعداد اللغة (إنجليزي فقط لضمان مصادر موثوقة)
wikipedia.set_lang("en")

CLEAN_RE = re.compile(r"\[[0-9]+\]")   # حذف مراجع ويكيبيديا [1], [2]


def clean(text: str) -> str:
    """تنظيف نص ويكيبيديا من المراجع والفواصل الغريبة."""
    if not text:
        return ""
    text = CLEAN_RE.sub("", text)
    text = text.replace("\n", " ").replace("  ", " ")
    return text.strip()


def split_into_facts(text: str):
    """تفكيك الفقرة إلى حقائق قصيرة مناسبة للفيديو."""
    if not text:
        return []

    sentences = re.split(r'\. |\? |\! ', text)
    facts = []

    for s in sentences:
        s = clean(s).strip()
        if len(s) > 30 and len(s) < 180:  # حقائق مناسبة للشورتس واللانج
            facts.append(s)

    return facts[:12]  # نكتفي بـ 12 حقيقة كحد أقصى


def fetch_wiki_facts(animal: str):
    """
    جلب فقرة مقدمة + جزء من السلوك + التغذية لو متاح.
    """
    try:
        page = wikipedia.page(animal)
        summary = clean(wikipedia.summary(animal, sentences=4))
        content = clean(page.content)

        facts = split_into_facts(summary)

        # fallback: لو ملقاش كفاية
        if len(facts) < 5:
            more = split_into_facts(content)
            facts.extend(more)

        facts = list(dict.fromkeys(facts))  # إزالة التكرار
        return facts[:12]

    except Exception as e:
        return []  # نخلي الـ content_generator هو اللي يعمل fallback
