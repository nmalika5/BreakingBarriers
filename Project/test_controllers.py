from unittest import TestCase
from model import connect_to_db, db, User, Language, Contact, Message, MessageLang, MessageContact
from server import app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import server
import subprocess
import MessageController, UserController, sentiment_analysis, yandex, server
from textblob import TextBlob

class MessageControllerTests(TestCase):
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

    def test_get_unique_langs(self):
        """Test getting of unique languages"""

        contacts = Contact.query.filter_by(user_id=6).all()

        unique_lang_dict = MessageController.get_unique_langs(contacts)
        self.assertEqual(unique_lang_dict, {4:  u'fr'})

    def test_translate_unique_langs(self):
        """Test translation of unique langs"""

        trans_msgs_dict = MessageController.translate_unique_langs({'2': 'es', '4': 'fr'}, 
                                                                    'hi', 'en', False, False)

        self.assertEqual(trans_msgs_dict, {'es': u'{hola}', 'fr': u'salut'})


    def test_add_trans_msg(self):
        """Test if a translated msg is added to MessageLang table"""

        translated_msg = MessageController.add_trans_msg(4, {'text': u'unittest', 'code': 200}, 1)
        query_db = MessageLang.query.filter_by(translated_message='unittest').first()

        self.assertIsNotNone(query_db)


    def test_add_sent_msg(self):
        """Test if a sent msg gets added to MessageContact table"""

        sent_msg = MessageController.add_sent_msg('queued', 15, 45)
        query_db = MessageContact.query.filter_by(message_id=45).first()

        self.assertIsNotNone(query_db)

    def test_numeric_contact_list(self):
        """Test if you get only string numbers out of the list of strings"""

        given_list = MessageController.get_numeric_list(['text', '2', '5', 'name'])
        self.assertEqual(given_list, ['2', '5'])


    def test_get_contact_objects(self):
        """Test if you can get a list of contact objects"""

        contacts = MessageController.get_contact_objects(['2'])
        self.assertEqual(contacts[0].contact_first_name, 'Contact2')
        self.assertEqual(contacts[0].contact_phone, '4153417706')
        self.assertEqual(contacts[0].user_id, 1)
        self.assertEqual(contacts[0].lang_id, 1)


class UserControllertests(TestCase):
    """Flask tests that show off mocking."""
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

    def test_contact_iteration(self):
        """Test contact iteration"""

        user_contacts = UserController.contact_iteration(3)

        self.assertEqual(user_contacts, [(u'4153417706', 5, u'Contact3', u'Test', 3),
                                        (u'4153417706', 5, u'Contact4', u'Test', 4)])


class SentimentAnalysistests(TestCase):
    """Flask tests that show off mocking."""
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

    def test_get_messages(self):
        """Test if you get messages"""

        messages = sentiment_analysis.get_messages(3)

        self.assertEqual(messages[0].message_text, 'This is a russian test message')
        self.assertEqual(messages[0].user_id, 3)
        self.assertEqual(messages[0].original_lang_id, 5)

    def test_msg_sentiment_analysis(self):
        """Test sentiment analysis of a message"""

        pos_messages = Message.query.filter_by(message_id=101).all()
        analyzed_messages = sentiment_analysis.analyze_messages(pos_messages)
        self.assertTrue(analyzed_messages[0].sentiment.polarity > 0.3)

        neg_messages = Message.query.filter_by(message_id=104).all()
        analyzed_messages = sentiment_analysis.analyze_messages(neg_messages)
        self.assertTrue(analyzed_messages[0].sentiment.polarity < -0.3)

    def test_categorize_msgs(self):
        """Test msgs categorization"""

        textblob_obj = TextBlob('Great')
        analyzed_msgs = sentiment_analysis.categorize_messages([textblob_obj])

        self.assertEqual(analyzed_msgs, [1, 0, 0])

    def test_get_contact_msgs(self):
        """Test getting contact's msgs"""

        contact_msgs = sentiment_analysis.get_contacts_msgs(7)
        
        self.assertEqual(contact_msgs[14][0].message_text, u'This is an english test message')

    def test_list_splitting(self):
        """Test list splitting"""

        given_list = [('Contact1', 2, 3, 0)]
        result = sentiment_analysis.break_list(given_list)

        self.assertEqual(result[0], ['Contact1'])
        self.assertEqual(result[1], [2])
        self.assertEqual(result[2], [3])
        self.assertEqual(result[3], [0])

class YandexTests(TestCase):
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

    def test_yandex_translation(self):
        """Test yandex translation"""

        message = yandex.translate_message('Hello my friend', 'en', 'fr')
        self.assertEqual(message["text"], [u"Bonjour, mon ami"])
        self.assertEqual(message["code"], 200)


    def test_caching_translation(self):
        """Test caching translation"""

        existing_message = yandex.translate_message('salut', 'fr', 'en')
        self.assertEqual(existing_message["text"], u"hi")
        self.assertEqual(existing_message["code"], 255)

class FlaskTests(TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_home(self):
        route = self.client.get('/')
        self.assertEqual(route.status_code, 200)
        self.assertIn('text/html', route.headers['Content-Type'])

    def test_register(self):
        route = self.client.get('/register')
        self.assertEqual(route.status_code, 200)

    def test_register(self):
        route = self.client.get('/login')
        self.assertEqual(route.status_code, 200)

    def test_chat(self):
        route = self.client.get('/users/1/chat')
        #if there's no user session, returns redirect
        self.assertEqual(route.status_code, 302)

    def test_user_profile(self):
        route = self.client.get('/users/1')
        #if there's no user session, returns redirect
        self.assertEqual(route.status_code, 302)



if __name__ == "__main__":
    import unittest

    unittest.main()