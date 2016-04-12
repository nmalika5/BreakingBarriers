"""Models and database functions for my project."""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import asc
import time
import os

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of my project."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    lang_id = db.Column(db.Integer, db.ForeignKey('languages.lang_id'), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)

    # Define relationship to user
    language = db.relationship("Language",
                           backref=db.backref("users", order_by=user_id))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s, phone_number=%s>" % (self.user_id, self.phone_number)
                                                                  
    def set_password(self, password):
        """Hash passwords"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check passwords"""

        return check_password_hash(self.password, password)

    def get_user_img(self):
        """Get user's image"""

        caching = time.time()

        return "/static/img/user%s.jpeg?%s" % (self.user_id, caching)


class Language(db.Model):
    """Language of a user on my website."""

    __tablename__ = "languages"

    lang_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lang_name = db.Column(db.String(30), nullable=False)
    yandex_lang_code = db.Column(db.String(2), nullable=False)

    
    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Lang id=%s lang name=%s, lang code = %s>" % (self.lang_id, 
                                                              self.lang_name,
                                                              self.lang_code,
                                                              )  
    
    @staticmethod                                                
    def lang_iteration():
        """Iterate through a list of languages"""
    
        language_list = Language.query.order_by(asc(Language.lang_name)).all()

        languages = []

        for lang in language_list:
            languages.append((lang.lang_id, lang.lang_name))

        return languages

class Contact(db.Model):
    """Contact info of a user."""

    __tablename__ = "contacts"

    contact_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    contact_first_name = db.Column(db.String(60), nullable=True)
    contact_last_name = db.Column(db.String(60), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    lang_id = db.Column(db.Integer, db.ForeignKey('languages.lang_id'))

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("contacts", order_by=contact_id))

    # Define relationship to language
    language = db.relationship("Language",
                            backref=db.backref("contacts", order_by=contact_id))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Contact contact_id=%s user_id=%s language_id=%s, \
                contact_phone=%s>" % (self.contact_id, self.user_id, self.lang_id, 
                                      self.contact_phone)

class Message(db.Model):
    """Message of a user."""

    __tablename__ = "messages"

    message_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    message_text = db.Column(db.String(1000), nullable=True)
    message_sent_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    original_lang_id = db.Column(db.Integer, db.ForeignKey('languages.lang_id'))
    
    languages = db.relationship("Language", secondary="messages_langs", backref="messages")
    contacts = db.relationship("Contact", secondary="messages_contacts", backref="messages")


    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("messages", order_by=message_id))

    # Define relationship to language
    language = db.relationship("Language", 
                                backref=db.backref("languages", order_by=message_id))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Message message_id=%s user_id=%s message=%s, \
                message sent=%s>" % (
                                                                self.message_id, 
                                                                self.user_id, 
                                                                self.message_text,
                                                                self.message_sent_at,
                                                                )
    # write a method that will return an english msg, returns an empty string if there's no english message

    def get_eng_msg(self):
        """ Message object -> string
        Returns an original msg but in english"""
        import yandex

        if self.original_lang_id == 1:
    
            return self.message_text

        trans_eng_msg = MessageLang.query.filter((MessageLang.lang_id==1) & (MessageLang.message_id==self.message_id)).first()
        
        if trans_eng_msg:
            
            return trans_eng_msg.translated_message

        else:

            translate_to_eng = yandex.translate_message(self.message_text, self.language.yandex_lang_code, 'en')
            eng_msg = ''.join(translate_to_eng['text'])

            fake_eng_msg = MessageLang(translated_message=eng_msg, message_status=270, lang_id=1, message_id=self.message_id)

            db.session.add(fake_eng_msg)
            db.session.commit()
            
            return eng_msg

        return ""

class MessageLang(db.Model):
    """Association table between messages and languages tables."""

    __tablename__ = "messages_langs"

    message_lang_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lang_id = db.Column(db.Integer, db.ForeignKey('languages.lang_id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.message_id'), nullable=False)
    translated_message = db.Column(db.String(1500), nullable=True)
    message_status = db.Column(db.Integer, nullable=True) 


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<message_lang_id=%s lang_id=%s, message_id=%s>" % (self.message_lang_id, 
                                                                  self.lang_id,
                                                                  self.message_id,
                                                                  )

class MessageContact(db.Model):
    """Association table between messages and contact tables."""

    __tablename__ = "messages_contacts"

    message_contact_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.contact_id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.message_id'), nullable=False)
    message_status = db.Column(db.String(30), nullable=True) 




    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<message_contact_id=%s, contact_id=%s, message_id=%s" % (
                                                                  self.message_contact_id, 
                                                                  self.contact_id,
                                                                  self.message_id,
                                                                  )


##############################################################################
# Helper functions

def connect_to_db(app, database):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    # app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get("DATABASE_URL", "postgresql:///myapp")
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app, os.environ.get("DATABASE_URL", "postgresql:///myapp"))
    print "Connected to DB."
