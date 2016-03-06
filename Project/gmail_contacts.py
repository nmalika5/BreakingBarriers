import gdata.gauth
import os
from lxml import etree
from urllib import urlencode
import requests
import json
import pickle
from model import Contact, db

CLIENT_ID=os.environ.get("CLIENT_ID")
CLIENT_SECRET=os.environ.get("CLIENT_SECRET")
SCOPE=os.environ.get("SCOPE")
USER_AGENT=os.environ.get("USER_AGENT")
CONTACTS_URL=os.environ.get("CONTACTS_URL")
REDIRECT_URI=os.environ.get("REDIRECT_URI")

def authorize_url(flask_session, user_id):
    """Create authorize url"""
    token = gdata.gauth.OAuth2Token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=SCOPE, user_agent=USER_AGENT)
    authorize_url = token.generate_authorize_url(redirect_uri=REDIRECT_URI)

    pickle.dump(token, open('token' + str(user_id) + '.p', 'wb'))
    flask_session['user_id'] = user_id
    return authorize_url


def get_contacts_name(elm):
    """Get contacts' names"""
    split_name = []
    for name in elm.findall('{http://www.w3.org/2005/Atom}title'):
        name = name.text
        if name != None:       
            split_name = name.split()
    
    return split_name


def get_contacts_phone(elm):
    """Get contacts' phones"""
    for phone_number in elm.findall('{http://schemas.google.com/g/2005}phoneNumber'):

        return phone_number.text


def parse_contacts(user, contacts_xml=None):
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
    root = etree.fromstring(contacts_xml.encode("utf-8"), parser)
    elms = root.findall("{http://www.w3.org/2005/Atom}entry")
    contacts = []
    
    for elm in elms:
        contact_name = get_contacts_name(elm)
        contact_phone = get_contacts_phone(elm)
        language = user.language.lang_id
        existing_contact = Contact.query.filter_by(user_id=user.user_id, contact_phone=contact_phone).all()
        if contact_phone != None:
            if not existing_contact:
                gmail_contact = Contact(contact_first_name=contact_name[0], 
                                    contact_last_name=contact_name[1],
                                    contact_phone=contact_phone, lang_id=language, user_id=user.user_id)
                db.session.add(gmail_contact)

    db.session.commit()

