from yandex_translate import YandexTranslate
import os

YANDEX_API_KEY=os.environ.get("YANDEX_API_KEY")
translate = YandexTranslate(YANDEX_API_KEY)

    
def translate_message(message_text, from_lang, to_lang):
    """Translates a message and returns a dict with keys text-for a msg and code-status"""

    lang_combo = from_lang + "-" + to_lang

    translate_text = translate.translate(message_text, lang_combo)
    
    return translate_text
