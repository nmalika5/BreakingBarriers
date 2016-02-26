from model import connect_to_db, db, User, Language, Contact, Message, MessageLang, MessageContact

def contact_iteration(user_id):
    """Iterate through a list of contacts"""

    user_contact_list = Contact.query.filter_by(user_id = user_id).all()

    contacts = []

    for contact in user_contact_list:
        contacts.append((contact.contact_phone, contact.language.lang_name, 
                         contact.contact_first_name, contact.contact_last_name, 
                         contact.contact_id))

    return contacts



