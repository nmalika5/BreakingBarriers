from yandex_translate import YandexTranslate

api_key = 'trnsl.1.1.20160208T195023Z.302d7000bf527427.e55e9fa77c97a0706b125efc605e8e90a40f20cb'
translate = YandexTranslate(api_key)

    
def translate_message(message_text, from_lang, to_lang):
    """Translates a message"""

    lang_combo = from_lang + "-" + to_lang

    return translate.translate(message_text, lang_combo)
    


