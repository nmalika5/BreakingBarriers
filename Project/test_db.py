from unittest import TestCase
from model import connect_to_db, db, User, Language, Contact, Message, MessageLang, MessageContact
from server import app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import server
import subprocess

class UserTests(TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        db = SQLAlchemy()

        connect_to_db(self.app, "postgresql:///testdb")

        subprocess.check_output("psql testdb < test_query.sql", shell=True)

        with self.app.test_request_context():

            db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_user_creation(self):
        """Test user creation"""

        new_user = User(email='unittest@test.com', first_name='Unittest',
                    last_name='Test', lang_id=4, phone_number='4153417706')

        db.session.add(new_user)
        db.session.commit()
        query_db = User.query.filter_by(email='unittest@test.com').first()
        self.assertIsNotNone(query_db)

    def test_user_edit(self):
        """Test user edit"""

        user = User.query.filter_by(user_id=1).one()
        user.last_name = 'Unittest'
        db.session.commit()
        self.assertEqual(user.last_name, 'Unittest')

    def test_find_user_contacts(self):
        """Find user's contacts"""

        user = User.query.filter_by(user_id=8).one()
        user_contacts = user.contacts

        self.assertEqual(user_contacts[0].contact_phone, '4153417706')
        self.assertEqual(user_contacts[0].contact_first_name, 'My Contact')
        self.assertEqual(user_contacts[0].contact_last_name, 'Test')
        self.assertEqual(user_contacts[0].lang_id, 4)

    def test_find_user_by_last_name(self):
        """Can we find a user in the sample data?"""

        user = User.query.filter(User.last_name == "Nikhmonova").first()
        self.assertEqual(user.last_name, "Nikhmonova")

    def test_user_img(self):
        """Test user's img"""

        user = User.query.filter_by(user_id=1).one()
        img = user.get_user_img()
        self.assertIn('/static/img/user1.jpeg?', img)


class MessageTests(TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        db = SQLAlchemy()

        connect_to_db(self.app, "postgresql:///testdb")

        subprocess.check_output("psql testdb < test_query.sql", shell=True)

        with self.app.test_request_context():

            db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_message_creation(self):
        """Test message creation"""

        new_message = Message(message_text='this is unittest', user_id=1, 
                      original_lang_id=1, message_sent_at='2016-02-24 18:01:18.903694')
        
        db.session.add(new_message)
        db.session.commit()

        query_db = Message.query.filter_by(message_text='this is unittest').first()
        self.assertIsNotNone(query_db)

    def test_find_message(self):
        """Find a message"""

        message = Message.query.filter_by(message_id=33).first()
        self.assertEqual(message.message_text, 'You are fantastic beyond measure.')

    def test_find_msg_langs(self):
        """Find translated langs of user's msg"""

        user_msg = Message.query.filter_by(message_id=107).one()
        trans_langs = user_msg.languages

        self.assertEqual(trans_langs[0].lang_name, 'Spanish')
        self.assertEqual(trans_langs[0].yandex_lang_code, 'es')

    def test_find_msg_contacts(self):
        """Find contacts of user's msg"""

        user_msg = Message.query.filter_by(message_id=107).one()
        msg_contacts = user_msg.contacts

        self.assertEqual(msg_contacts[0].contact_id, 42)
        self.assertEqual(msg_contacts[0].lang_id, 2)        


class ContactTests(TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        db = SQLAlchemy()

        connect_to_db(self.app, "postgresql:///testdb")

        subprocess.check_output("psql testdb < test_query.sql", shell=True)

        with self.app.test_request_context():

            db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_contact_creation(self):
        """Test user creation"""

        new_contact = Contact(contact_first_name='Unittest',
                              contact_last_name='Test', lang_id=2, user_id=1,
                              contact_phone='4153417706')

        db.session.add(new_contact)
        db.session.commit()

        query_db = Contact.query.filter_by(contact_first_name='Unittest').first()
        self.assertIsNotNone(query_db)

    def test_contact_edit(self):
        """Test user edit"""

        contact = Contact.query.filter_by(contact_phone='1111111111').one()
        contact.contact_first_name = 'Unittestedit'
        db.session.commit()
        reloaded_contact = Contact.query.filter_by(contact_phone='1111111111').one()
        self.assertEqual(reloaded_contact.contact_first_name, 'Unittestedit')

    def test_contact_deletion(self):
        """Test contact deletion"""

        contact = Contact.query.filter_by(contact_phone='1111111111').one()
        db.session.delete(contact)
        db.session.commit()

        query_db = Contact.query.filter_by(contact_phone='1111111111').first()
        self.assertIsNone(query_db)

    def test_find_contact(self):
        """Find an existing contact"""

        existing_contact = Contact.query.filter_by(contact_id=1).one()
        self.assertEqual(existing_contact.contact_phone, '4153417706')
        self.assertEqual(existing_contact.lang_id, 1)        

class LanguageTests(TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        db = SQLAlchemy()

        connect_to_db(self.app, "postgresql:///testdb")

        subprocess.check_output("psql testdb < test_query.sql", shell=True)

        with self.app.test_request_context():

            db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_find_language(self):
        """Can we find a user in the sample data?"""

        language = Language.query.filter(Language.lang_id == 4).one()
        self.assertEqual(language.lang_name, "French")

    def test_unknown_language(self):
        """Test unknown language"""

        unknown_lang = Language.query.filter_by(lang_name='Bla').first()
        self.assertIsNone(unknown_lang)


class MessageLangTests(TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        db = SQLAlchemy()

        connect_to_db(self.app, "postgresql:///testdb")

        subprocess.check_output("psql testdb < test_query.sql", shell=True)

        with self.app.test_request_context():

            db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_msg_lang_creation(self):
        """Test creation to MessageLang table"""

        new_trans_msg = MessageLang(lang_id=4,
                              message_id=15, translated_message='Au revoir mon ami', 
                              message_status=200)

        db.session.add(new_trans_msg)
        db.session.commit()

        query_db = MessageLang.query.filter_by(translated_message='Au revoir mon ami').first()
        self.assertIsNotNone(query_db)

    def test_find_msg(self):
        """Test to find msg from MessageLang table"""

        existing_message = MessageLang.query.filter_by(translated_message='what a beautiful day!').one()
        self.assertEqual(existing_message.message_status, 200)
        self.assertEqual(existing_message.lang_id, 1)


class MessageContactsTests(TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        db = SQLAlchemy()
        connect_to_db(self.app, "postgresql:///testdb")

        subprocess.check_output("psql testdb < test_query.sql", shell=True)
        with self.app.test_request_context():

            db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_msg_contact_creation(self):
        """Test creation to MessageContact table"""

        new_record = MessageContact(contact_id=38,
                                    message_id=109, 
                                    message_status='queued')

        db.session.add(new_record)
        db.session.commit()

        query_db = MessageContact.query.filter_by(contact_id=38).first()
        self.assertIsNotNone(query_db)
        self.assertEqual(query_db.contact_id, 38)
        self.assertEqual(query_db.message_id, 109)
        self.assertEqual(query_db.message_status, 'queued')


    def test_find_msg_contact(self):
        """Test to find msg from MessageContact table"""

        existing_message = MessageContact.query.filter_by(message_id=101).one()
        self.assertEqual(existing_message.contact_id, 18)
        self.assertEqual(existing_message.message_status, 'queued')



if __name__ == "__main__":
    import unittest

    unittest.main()