from __future__ import division
from textblob import TextBlob
from model import connect_to_db, db, User, Language, Contact, Message, MessageLang, MessageContact


def get_messages(user_id):
    """ int -> [] of message objects 
        Get user's messages:
    """
    user_message_list = Message.query.filter_by(user_id = user_id).all()

    messages = []

    for message in user_message_list:
        messages.append(message)
    
    return messages

def analyze_messages(messages):
    """ [] of msg objects -> [] of textblob objects    
        Do sentiment analysis on user's messages
    """

    sentiment_list = []

    for message in messages:
        eng_message = message.get_eng_msg()
        if eng_message:
            sentiment_msg = TextBlob(eng_message)
            sentiment_list.append(sentiment_msg)

    return sentiment_list

def categorize_messages(sentiment_list):
    """ [] of textblob objects -> 3 ints in a []
    Categorize messages into 3 sections"""

    positive = 0
    negative = 0
    neutral = 0
    endpoint = float(1) / 3

    for elm in sentiment_list:
        if elm.sentiment.polarity > endpoint:
            positive += 1
        elif elm.sentiment.polarity < -endpoint:
            negative += 1   
        else:
            neutral += 1

    return [positive, negative, neutral]


def get_contacts_msgs(user_id):
    """int -> dict with key as an int & value as a [] of Message objects"""

    contacts = Contact.query.filter_by(user_id=user_id).all()
    contact_dict = {}

    for contact in contacts:
        contact_dict[contact.contact_id] = contact.messages

    return contact_dict

def get_contacts(contact_dict):
    """dict with key-int & value - [] of Message objects -> [] of lists"""

    output_list = []

    for contact_id in contact_dict:
        positive = 0
        negative = 0
        neutral = 0
        endpoint = float(1) / 3

        contact = Contact.query.filter_by(contact_id=contact_id).one()
        contact_fname = contact.contact_first_name
        contact_lname = contact.contact_last_name
        contact_name = contact_fname + " " + contact_lname
        for contact_msg in contact_dict[contact_id]:
            eng_message = contact_msg.get_eng_msg()
            if eng_message:
                sentiment_msg = TextBlob(eng_message)
                if sentiment_msg.sentiment.polarity > endpoint:
                    positive += 1
                elif sentiment_msg.sentiment.polarity < -endpoint:
                    negative += 1   
                else:
                    neutral += 1
        output_list.append((contact_name, positive, negative, neutral))

    return output_list

def break_list(output_list):
    """[] of tuple objects -> [] of four []"""

    contact_names = []
    positive_msgs = []
    negative_msgs = []
    neutral_msgs = []

    for elm in output_list:
        contact_names.append(elm[0])
        positive_msgs.append(elm[1])
        negative_msgs.append(elm[2])
        neutral_msgs.append(elm[3])

    return [contact_names, positive_msgs, negative_msgs, neutral_msgs]


