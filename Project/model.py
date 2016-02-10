"""Models and database functions for my project."""

from flask_sqlalchemy import SQLAlchemy

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
    message_returned = db.Column(db.String(1000), nullable=True)
    message_status = db.Column(db.Integer, nullable=True) 
    message_sent_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # original_lang_id = db.Column(db.Integer, db.ForeignKey('languages.lang_id'))
    
    languages = db.relationship("Language", secondary="messages_langs", backref="messages")
    contacts = db.relationship("Contact", secondary="messages_contacts", backref="messages")


    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("messages", order_by=message_id))

    # # Define relationship to language
    # language = db.relationship("Language", 
    #                             backref=db.backref("messages", order_by=message_id))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Message message_id=%s user_id=%s message_status=%s, message=%s, \
                message sent=%s>" % (
                                                                self.message_id, 
                                                                self.user_id, 
                                                                self.message_status,
                                                                self.message_text,
                                                                self.message_sent_at,
                                                                )

class MessageLang(db.Model):
    """Association table between messages and languages tables."""

    __tablename__ = "messages_langs"

    message_lang_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lang_id = db.Column(db.Integer, db.ForeignKey('languages.lang_id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.message_id'), nullable=False)



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



    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<message_contact_id=%s, contact_id=%s, message_id=%s" % (
                                                                  self.message_contact_id, 
                                                                  self.contact_id,
                                                                  self.message_id,
                                                                  )


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///myapp'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
