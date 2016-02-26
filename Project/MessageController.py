from model import connect_to_db, db, User, Language, Contact, Message, MessageLang, MessageContact
from sqlalchemy import distinct, func
import yandex, twilio_api

def get_unique_langs(contacts):
    """[] of Contact class -> dict with key as int & value string
    Get a dict of unique langs"""

    #making a unique list of contacts' langs
    unique_lang_dict = {}
    for contact in contacts:
        contact_lang = contact.language.yandex_lang_code
        unique_lang_dict[contact.language.lang_id] = contact_lang

    return unique_lang_dict #returns a dict with key as int & value string

def translate_unique_langs(unique_lang_dict, user_message, lang_code, message_id, add_msg):
    """ dict, string, string, int -> dict with key as string & value-string
    Translate unique langs"""

    trans_msgs_dict = {}
    for unique_lang_id in unique_lang_dict:
        unique_lang_code = unique_lang_dict[unique_lang_id]
        trans_msg = yandex.translate_message(user_message, lang_code, unique_lang_code)
        trans_text = trans_msg['text']
        trans_msgs_dict[unique_lang_code] = trans_text

        if add_msg:
            msg_lang = add_trans_msg(unique_lang_id, trans_msg, message_id)

    return trans_msgs_dict 


def add_trans_msg(unique_lang_id, trans_msg, message_id):
    """Add translated msg to MessageLang table"""

    trans_text = trans_msg['text']
    trans_status = trans_msg['code']
    msg_lang = MessageLang(lang_id=unique_lang_id, message_id=message_id, translated_message=trans_text,
                               message_status=trans_status)
    
    db.session.add(msg_lang)
    db.session.commit()

def send_trans_texts(contacts, trans_msgs_dict, message_id):
    """ [], dict, int -> None
    Send translated texts to contacts"""

    for contact in contacts:
        contact_lang = contact.language.yandex_lang_code
        msg = twilio_api.send_message(trans_msgs_dict[contact_lang], contact.contact_phone)
        contact_msg = add_sent_msg(msg.status, contact.contact_id, message_id)


def add_sent_msg(msg_status, contact_id, message_id):
    """Add sent msgs to MessageContact table"""

    contact_msg = MessageContact(contact_id=contact_id, message_id=message_id, 
                                 message_status=msg_status)

    db.session.add(contact_msg)
    db.session.commit()


def get_numeric_list(contacts):
    """[] of string -> [] of int
    Get only integers out of the list"""

    numeric_list = [i for i in contacts if i.isdigit()]

    return numeric_list

def get_contact_objects(numeric_list):
    """Get a list of contact objects"""

    contact_list = []

    for contact_id in numeric_list:
        contact = Contact.query.filter_by(contact_id=contact_id).one()
        contact_list.append(contact)

    return contact_list

