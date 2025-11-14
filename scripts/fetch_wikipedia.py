import wikipedia
import warnings
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", category=UserWarning)

def get_wikipedia_summary(animal_name: str) -> str:
    """
    يرجّع ملخص Wikipedia الحقيقي عن الحيوان.
    لو الحيوان مش موجود أو فيه خطأ، يرجّع None.
    """

    try:
        wikipedia.set_lang("en")

        # ابحث عن الصفحة
        results = wikipedia.search(animal_name, results=1)
        if not results:
            return None

        page_title = results[0]

        # جيب الصفحة
        page = wikipedia.page(page_title, auto_suggest=False)

        # ملخص جاهز
        summary = page.summary.strip()

        # لو الملخص أقصر من اللازم، هنجرب نجيب الفقرات الأولى من الـ HTML
        if len(summary) < 120:
            html = page.html()
            soup = BeautifulSoup(html, features="html.parser")
            paragraphs = soup.find_all("p")
            for p in paragraphs:
                txt = p.get_text().strip()
                if len(txt) > 120:
                    summary = txt
                    break

        return summary

    except Exception as e:
        return None


def get_wikipedia_facts(animal_name: str, num_facts: int = 10) -> list:
    """
    يرجّع قائمة حقائق حقيقية مستخرجة من ويكيبيديا مباشرة.
    """

    summary = get_wikipedia_summary(animal_name)
    if not summary:
        return []

    # تقسيم النص لجمل
    sentences = [
        s.strip()
        for s in summary.replace("\n", " ").split(".")
        if len(s.strip()) > 20
    ]

    # خذ أول عدد من الجمل كحقائق
    facts = sentences[:num_facts]

    # fallback لو ويكيبيديا راجعة قليل
    if len(facts) < num_facts:
        facts = facts + ["No more factual data available from Wikipedia."] * (num_facts - len(facts))

    return facts
