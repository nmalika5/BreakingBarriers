from yandex_translate import YandexTranslate
import os

YANDEX_API_KEY=os.environ.get("YANDEX_API_KEY")
translate = YandexTranslate(YANDEX_API_KEY)

    
def translate_message(message_text, from_lang, to_lang):
    """Translates a message"""

    lang_combo = from_lang + "-" + to_lang

    return translate.translate(message_text, lang_combo)['text']
    


