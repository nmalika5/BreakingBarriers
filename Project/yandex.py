from yandex_translate import YandexTranslate
import os
from sqlalchemy import func


YANDEX_API_KEY=os.environ.get("YANDEX_API_KEY")
translate = YandexTranslate(YANDEX_API_KEY)

    
def translate_message(message_text, from_lang, to_lang):
    """Translates a message and returns a dict with keys text-for a msg and code-status"""

    from model import db, Contact, Message, MessageLang, Language

    lang_combo = from_lang + "-" + to_lang

    to_lang_id = Language.query.filter_by(yandex_lang_code=to_lang).one()
    from_lang_id = Language.query.filter_by(yandex_lang_code=from_lang).one()
    
    existing_trans_msg = db.session.query(MessageLang) \
                                .join(Message, MessageLang.message_id == Message.message_id) \
                                .filter((MessageLang.lang_id == to_lang_id.lang_id) & (Message.original_lang_id == from_lang_id.lang_id) \
                                    & (Message.message_text == message_text)).first()

    
    if existing_trans_msg is None:
        translate_text = translate.translate(message_text, lang_combo)

        return translate_text
        

    elif existing_trans_msg.translated_message:
        msg_dict = { "text" : existing_trans_msg.translated_message,
                    "code" : 255
                   }
        
        return msg_dict

    else:
        translate_text = translate.translate(message_text, lang_combo)

        return translate_text

