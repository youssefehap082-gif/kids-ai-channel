
from deep_translator import GoogleTranslator

def translate_text(text, languages=["es","fr","de","pt","it"]):
    translations = {}
    for lang in languages:
        try:
            translations[lang] = GoogleTranslator(source='en', target=lang).translate(text)
        except:
            translations[lang] = text
    return translations
