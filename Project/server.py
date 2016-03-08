from jinja2 import StrictUndefined
import flask
from flask import Flask, render_template, request, flash, redirect, session, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Language, Contact, Message, MessageLang, MessageContact
from sqlalchemy import distinct, func, desc
import yandex, twilio_api, MessageController, UserController, sentiment_analysis
import json
from gevent import monkey; monkey.patch_all()
import datetime
import os
from xml.etree import ElementTree
import gmail_contacts
import pickle
import gdata.contacts.client
import gmail_contacts
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin



# The socket.io namespace
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    def room_name(self, user1_id, user2_id):
        """Create a unique room for each pair of users"""

        if user1_id < user2_id:
            room_name = str(user1_id) + "," + str(user2_id)
        else:
            room_name = str(user2_id) + "," + str(user1_id)

        return str(room_name)
    
    def on_nickname(self, nickname):
        """Handle nicknames"""

        user1 = User.query.filter_by(user_id=nickname['user1']).one()
        user2 = User.query.filter_by(user_id=nickname['user2']).one()
        
        self.environ.setdefault('nicknames', []).append(nickname['nickname'])
        self.socket.session['nickname'] = nickname['nickname']

        room = self.room_name(user1.user_id, user2.user_id)

        self.emit_to_room(room, 'nicknames', self.socket.session['nickname'],
                          self.environ['nicknames'])
        self.emit_to_room(room, 'announcement', self.socket.session['nickname'], 
                          '%s has connected' % nickname['nickname'])
        self.join(room)


    def on_user_message(self, trans_msg):
        """Translate a message and send it to the room"""

        user1 = User.query.filter_by(user_id=trans_msg['user1']).one()
        user2 = User.query.filter_by(user_id=trans_msg['user2']).one()

        trans_msg = yandex.translate_message(trans_msg['message'], 
                                        user1.language.yandex_lang_code, 
                                        user2.language.yandex_lang_code)['text']

        trans_msg = ''.join(trans_msg)

        room = self.room_name(user1.user_id, user2.user_id)
        self.emit_to_room(room, 'msg_to_room', 
                        self.socket.session['nickname'], 
                        trans_msg)


    def recv_message(self, message):
        """Receive a message"""
        print "PING!!!", message


UPLOAD_FOLDER = 'static/img'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
print type(app)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
        
    return render_template("home.html")


@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    languages = Language.lang_iteration()
    
    return render_template("register_form.html", languages=languages)


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form.get("email")
    password = request.form.get("password")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    lang_id = request.form.get("lang_id")
    phone_number = request.form.get("phone")


    new_user = User(email=email, first_name=first_name,
                    last_name=last_name, lang_id=lang_id, phone_number=phone_number)

    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return redirect("/") 

@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("home.html")

@app.route('/check_login')
def check_login():
    """Check if user is logged in."""

    if not session:
        flash("Please log in.")
        return redirect("/")
    elif "user_id" in session:
        return redirect("users/%s" % session["user_id"])
    else:
        flash("Please log in.")
        return redirect("/")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/register")

    if not user.check_password(password):
        flash("Incorrect password")
        return redirect("/")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/users/%s" % user.user_id)

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")

@app.route("/users/<int:user_id>/chat")
def user_list(user_id):
    """Show list of possible chat rooms."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    users = User.query.all()

    return render_template("chat_rooms.html", users=users, user_id=user_id)


@app.route("/users/<int:user_id>", methods=["GET"])
def user_detail(user_id):
    """Show info about user."""
    
    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    user = User.query.get(user_id)
    
    contacts = UserController.contact_iteration(user_id)

    languages = Language.lang_iteration()

    existing_message = ""

    if len(contacts) == 0:
        flash("The user has no contacts, you need to add one")
        return redirect("/users/%s/add_contact" % user_id)

    return render_template("contact_edit.html", user=user, 
                            user_id=user_id, contacts=json.dumps(contacts),
                            contact_objects = contacts, languages=json.dumps(languages), 
                            existing_message=existing_message, user_img=user.get_user_img())


@app.route("/users/<int:user_id>/edit_user", methods=["GET"])
def show_user_edit(user_id):
    """Edit user's info."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    user = User.query.get(user_id)

    languages = Language.lang_iteration()
 
    return render_template("user_edit.html", user=user, user_img=user.get_user_img(), languages=languages)


@app.route("/users/<int:user_id>/edit_user", methods=["POST"])
def user_edit(user_id):
    """Edit user's info."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    user = User.query.filter_by(user_id=user_id).one()

    user_img = request.files['img']
    email = request.form.get("email")
    password = request.form.get("password")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    lang_id = request.form.get("lang_id")
    phone_number = request.form.get("phone_number")

    if user_img:
        filename = "user%s.jpeg" % user.user_id
        user_img.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], filename))

    if user:
        if first_name: 
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if password: 
            user.password = password
            user.set_password(password)
        if lang_id:
            user.lang_id = lang_id
        if phone_number:
            user.phone_number = phone_number
    
    db.session.commit()

    return redirect("/users/%s" % user_id)


@app.route("/users/<int:user_id>/add_contact", methods=['GET'])
def show_contact_form(user_id):
    """Show form for contact signup."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    user = User.query.get(user_id)

    languages = Language.lang_iteration()

    return render_template("contact_add.html", user_id=user_id, languages=languages)


@app.route("/users/<int:user_id>/add_contact", methods=["POST"])
def add_contact(user_id):
    """Add a contact."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    language = request.form["lang_id"]
    phone = request.form["phone"]

    contact = Contact(contact_first_name=first_name, contact_last_name=last_name,
                    contact_phone=phone, user_id=user_id, lang_id=language)
    
    db.session.add(contact)

    db.session.commit()

    return redirect("/users/%s" % user_id)


@app.route("/users/<int:user_id>/contacts/<int:contact_id>", methods=["DELETE"])
def delete_contact(user_id, contact_id):
    """Delete a contact."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    contact_id = Contact.query.filter_by(contact_id=contact_id).one()
    
    flash("Contact deleted.")
    db.session.delete(contact_id)

    db.session.commit()

    return ('', 204) 

@app.route("/users/<int:user_id>/contacts/<int:contact_id>", methods=["PUT"])
def edit_contact(user_id, contact_id):
    """Edit a contact."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    contact = Contact.query.filter_by(contact_id=contact_id).one()
    request.data = json.loads(request.data)
    contact_fname = request.data["fname"]
    contact_lname = request.data["lname"]
    language = request.data["language"]
    phone = request.data["phone"]

    if contact:
        if contact_fname: 
            contact.contact_first_name = contact_fname
        if contact_lname:
            contact.contact_last_name = contact_lname
        if language:
            lang = Language.query.filter_by(lang_id=language).one()
            contact.lang_id = lang.lang_id
        if phone:
            contact.contact_phone = phone
    
    flash("Contact updated.")
    db.session.commit()

    return ('', 204) 


@app.route("/users/<int:user_id>/send_text/submit", methods=["POST"])
def submit_text_form(user_id):
    """Send message"""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    user_message = request.form.get("text")
    contact_id_list = MessageController.get_numeric_list(request.form.keys())

    contacts = MessageController.get_contact_objects(contact_id_list)

    user_id = session['user_id']
    user = User.query.filter_by(user_id=user_id).all()[0]
    original_lang_id = user.language.lang_id
    msg_sent_at = datetime.datetime.now()

    message = Message(message_text=user_message, user_id=user_id, 
                      original_lang_id=original_lang_id, message_sent_at=msg_sent_at)
    
    flash("Message added.")
    db.session.add(message)
    db.session.commit()


    lang_code = user.language.yandex_lang_code
    contact_langs = []

    unique_lang_dict = MessageController.get_unique_langs(contacts)

    translate_langs_dict = MessageController.translate_unique_langs(unique_lang_dict,
                                                                    user_message, 
                                                                    lang_code, message.message_id,
                                                                    True)


    MessageController.send_trans_texts(contacts, translate_langs_dict,
                                      message.message_id)

    flash('The translated texts have been sent')
    return redirect("/users/%s" % user_id)

@app.route("/users/<int:user_id>/messages", methods=["GET"])
def message_list(user_id):
    """Show info about user's messages."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    user_messages = db.session.query(Message).filter(Message.user_id == user_id).order_by(desc(Message.message_id)).limit(10).all()

    messages = []

    if len(user_messages) == 0:
        flash("The user has no messages")
        return redirect("/users/%s/send_text" % user_id)
        

    for message in user_messages:
        messages.append((message.language.lang_name, message.message_text, 
                         message.message_sent_at))


    return render_template("message_list.html", messages=messages, user_id=user_id)

@app.route('/users/<int:user_id>/messages/message-types.json')
def messages_types_data(user_id):
    """Return data about messages emotions."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    messages = sentiment_analysis.get_messages(user_id) 

    sentiment_list = sentiment_analysis.analyze_messages(messages)

    arranged_list = sentiment_analysis.categorize_messages(sentiment_list)

    data_list_of_dicts = {
        'arranged_list': [
            {
                "value": arranged_list[0],
                "color": "#F7464A",
                "highlight": "#FF5A5E",
                "label": "Positive messages"
            },
            {
                "value": arranged_list[1],
                "color": "#46BFBD",
                "highlight": "#5AD3D1",
                "label": "Negative messages"
            },
            {
                "value": arranged_list[2],
                "color": "#FDB45C",
                "highlight": "#FFC870",
                "label": "Neutral messages"
            }
        ]
    }
    return jsonify(data_list_of_dicts)

@app.route('/users/<int:user_id>/messages/contact-messages.json')
def contact_messages_data(user_id):
    """Return contact's messages data."""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    contact_msgs = sentiment_analysis.get_contacts_msgs(user_id)
    sentiment_list = sentiment_analysis.get_contacts(contact_msgs)
    arranged_list = sentiment_analysis.break_list(sentiment_list)
    print arranged_list

    data_dict = {
        "labels": arranged_list[0],
        "datasets": [
            {
                "label": "Positive messages",
                "fillColor": "#F7464A",
                "strokeColor": "rgba(220,220,220,0.8)",
                "highlightFill": "rgba(151,187,205,0.75)",
                "highlightStroke": "rgba(220,220,220,1)",
                "data": arranged_list[1]
            },
            {
                "label": "Negative messages",
                "fillColor": "#46BFBD",
                "strokeColor": "rgba(151,187,205,0.8)",
                "highlightFill": "rgba(151,187,205,0.75)",
                "highlightStroke": "#46BFBD",
                "data": arranged_list[2]
            },
            {
                "label": "Neutral messages",
                "fillColor": "#FDB45C",
                "strokeColor": "rgba(151,187,205,0.8)",
                "highlightFill": "rgba(151,187,205,0.75)",
                "highlightStroke": "#C0C0C0",
                "data": arranged_list[3]
            }
        ]
    };
    return jsonify(data_dict)

@app.route("/users/<int:user_id>/send_text/preview", methods=["POST"])
def preview_message(user_id):
    """Preview translated message"""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    user_message = request.form.get("text")
    contact_id_list = MessageController.get_numeric_list(request.form.getlist("contactIds"))

    contacts = MessageController.get_contact_objects(contact_id_list)

    if user_message:
        user_id = session['user_id']
        user = User.query.filter_by(user_id=user_id).all()[0]
        lang_code = user.language.yandex_lang_code 

        unique_lang_dict = MessageController.get_unique_langs(contacts)
        
        translate_langs_dict = MessageController.translate_unique_langs(unique_lang_dict,
                                                                        user_message, 
                                                                        lang_code, 
                                                                        False,
                                                                        False)
    
    trans_msgs = []
    for contact in contacts:
        contact_lang = contact.language.lang_name
        contact_lang_code = contact.language.yandex_lang_code
        contact_name = contact.contact_first_name + " " + contact.contact_last_name
        trans_msg = translate_langs_dict[contact_lang_code]
        trans_msgs.append((trans_msg, contact_name, contact_lang))

    return render_template('preview_table.html', trans_msgs=trans_msgs)

@app.route("/", methods=["POST", "GET"])
def send_text():
    """Receive text via Twilio"""
    
    contact_phone = request.values.get("From", None)
    response_message = request.values.get("Body", None)

    message_status = request.values.get("SmsStatus", None)


    if contact_phone != None:
        contact_phone = contact_phone[2:]
        contacts = Contact.query.filter_by(contact_phone=contact_phone).all()
        contact_id_list = []

        for contact in contacts:
            contact_id_list.append(contact.contact_id)
        msg_id = db.session.query(func.max(MessageContact.message_id)).filter(MessageContact.contact_id.in_(contact_id_list)).one()
        msg = Message.query.filter_by(message_id=msg_id).one()
        user = msg.user
        user_phone = user.phone_number
        to_lang = user.language.yandex_lang_code
        # all contacts that belong to that user and get a first one that matches the phone number
        from_contact = Contact.query.filter((Contact.user_id==user.user_id) & (Contact.contact_phone==contact_phone)).first()
        from_lang = from_contact.language.yandex_lang_code
        translated_resp_msg = yandex.translate_message(response_message, from_lang, to_lang)['text']
        twilio_api.send_message(translated_resp_msg, user_phone)

        return ('', 204)

    else:
        render_template('home.html')


@app.route("/users/<int:user_id>/contacts", methods=["POST", "GET"])
def redirect_gmail(user_id):
    """Redirect the user to gmail access page"""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user_id:
        return redirect("/users/%s" % session['user_id'])

    authorized_url = gmail_contacts.authorize_url(flask.session, user_id)

    return json.dumps(authorized_url)

@app.route("/user_contacts", methods=["POST", "GET"])
def redirect_app():
    """Redirect to my app after gmail"""

    key = request.args.get("code")
    
    if key:
        user_id = flask.session['user_id']
        user = User.query.get(user_id)
        token = pickle.load(open('token' + str(user_id) + '.p', 'rb'))
        token.get_access_token(key)
        client = gdata.contacts.client.ContactsClient(source='appname')
        client = token.authorize(client)
        feed = client.GetContacts()
        contacts = gmail_contacts.parse_contacts(user, str(feed))

        return redirect("/users/%s" % user.user_id)

@app.route("/user_images", methods=["POST", "GET"])
def show_users_imgs():
    "Show user's images"

    user_img = pickle.load(open('token' + str(user_id) + '.p', 'rb'))

@app.route('/users/<int:user1>/chat/<int:user2>')
def chat(user1, user2):
    """Renders chat for each pair of users"""

    if 'user_id' not in session:
        return redirect("/")
    elif session['user_id'] != user1:
        return redirect("/users/%s" % session['user_id'])

    return render_template('chat.html', user1=user1, user2=user2)

@app.route("/socket.io/<path:path>")
def run_socketio(path):
    """Runs sockets"""

    socketio_manage(request.environ, {'': ChatNamespace})


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo

    DebugToolbarExtension(app)

    connect_to_db(app, 'postgres:///myapp')

    print 'Listening on http://localhost:5000'
    app.debug = True
    import os
    from werkzeug.wsgi import SharedDataMiddleware
    flask_app = app
    app = SharedDataMiddleware(app, {
        '/': os.path.join(os.path.dirname(__file__), 'static')
        })
    from socketio.server import SocketIOServer
    SocketIOServer(('0.0.0.0', 5000), app,
        resource="socket.io", policy_server=False).serve_forever()


    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

