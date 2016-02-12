"""Text Translator."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Language, Contact, Message, MessageLang, MessageContact

from sqlalchemy import distinct

import yandex

import twilio_api

app = Flask(__name__)

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

    language_list = Language.query.all()

    languages = []

    for lang in language_list:
        languages.append((lang.lang_id, lang.lang_name))
    
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

    new_user = User(email=email, password=password, first_name=first_name,
                    last_name=last_name, lang_id=lang_id, phone_number=phone_number)

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % email)
    return redirect("/login") 

@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email, password=password).first()

    if not user:
        flash("No such user")
        return redirect("/register")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/users/%s/send_text" % user.user_id)
#if there're no contacts, redirect to profile to add contacts

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")

# USELESS
@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<int:user_id>", methods=["GET"])
def user_detail(user_id):
    """Show info about user."""
 
    user = User.query.get(user_id)
    user_contact_list = Contact.query.filter_by(user_id = user_id).all()

    contacts = []

    if len(user_contact_list) == 0:
        flash("The user has no contacts")
        return redirect("/users/%s/add_contact" % user_id)

    for contact in user_contact_list:
        contacts.append((contact.contact_phone, contact.language.lang_name, 
                         contact.contact_first_name))

    return render_template("user_profile.html", user=user, contacts=contacts, 
                            user_id=user_id)



    #vars = usercontroller.sstuff(hjhjgjl)

@app.route("/users/<int:user_id>/edit_user", methods=["GET"])
def show_user_edit(user_id):
    """Edit user's info."""

    return render_template("user_edit.html", user_id=user_id, first_name=first_name,
                            last_name=last_name, email= email, password=password)


@app.route("/users/<int:user_id>/edit_user", methods=["POST"])
def user_edit(user_id):
    """Edit user's info."""

    user = User.query.get(user_id)

    if user:
            user[0].first_name = first_name
            user[1].last_name = last_name
            user[2].email = email
            user[3].password = password
            user[4].lang_id = lang_id
            user[5].phone_number= phone_number

    db.session.commit()

    return redirect("/users/%s" % user_id)


@app.route("/users/<int:user_id>/add_contact", methods=['GET'])
def show_contact_form(user_id):
    """Show form for contact signup."""

    user = User.query.get(user_id)
    language_list = Language.query.all()

    languages = []

    for lang in language_list:
        languages.append((lang.lang_id, lang.lang_name))
    return render_template("contact_add.html", user_id=user_id, languages=languages)


@app.route("/users/<int:user_id>/add_contact", methods=["POST"])
def add_contact(user_id):
    """Add a contact."""

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    language = request.form["lang_id"]
    phone = request.form["phone"]

    contact = Contact(contact_first_name=first_name, contact_last_name=last_name,
                    contact_phone=phone, user_id=user_id, lang_id=language)
    
    flash("Contact added.")
    db.session.add(contact)

    db.session.commit()

    return redirect("/users/%s" % user_id)

# @app.route("/users/<int:user_id>/messages", methods=["GET"])
# def message_list(user_id):
#     """Show info about user's messages."""

#     user_message = Message.query.filter_by(user_id=user_id, message_id=message_id.all()

#     return render_template("message_list.html")

#TODO send text route, GET, show form

@app.route("/users/<int:user_id>/send_text", methods=["GET"])
def show_text_form(user_id):
    """Show send message form"""

    user_contact_list = Contact.query.filter_by(user_id = user_id).all()

    contacts = []

    if len(user_contact_list) == 0:
        flash("The user has no contacts, you need to add one")
        

    for contact in user_contact_list:
        contacts.append((contact.contact_phone, contact.language.lang_name, 
                         contact.contact_first_name))

    existing_message = ""

    return render_template("message_form.html", existing_message=existing_message, 
                            user_id=user_id, contacts=contacts)

@app.route("/users/<int:user_id>/send_text/submit", methods=["POST"])
def submit_text_form(user_id):
    """Send message"""

    user_message = request.form.get("text")

    if user_message:
        user_id = session['user_id']
        user = User.query.filter_by(user_id=user_id).all()[0]
        print user

        contacts = user.contacts

        lang_code = user.language.yandex_lang_code
        trans_msgs = []
        contact_langs = []

        for contact in contacts:
            contact_lang = contact.language.yandex_lang_code
            contact_langs.append(contact_lang)
        unique_list_lang = list(set(contact_langs))
        
        trans_msgs_dict = {}
        for unique_lang in unique_list_lang:
            trans_msgs_dict[unique_lang] = yandex.translate_message(user_message, lang_code, unique_lang)
        
        contact_dict = {}
        for contact in contacts:
            contact_lang = contact.language.yandex_lang_code
            contact_dict[contact.contact_id] = trans_msgs_dict[contact_lang]
            twilio_api.send_message(trans_msgs_dict[contact_lang], contact.contact_phone)
    
    flash('The translated texts have been sent')
    return redirect("/users/%s" % user_id)


@app.route("/users/<int:user_id>/send_text/preview", methods=["POST"])
def preview_message(user_id):
    """Preview translated message"""

    user_message = request.form.get("text")

    if user_message:
        user_id = session['user_id']
        user = User.query.filter_by(user_id=user_id).all()[0]

        contacts = user.contacts

        lang_code = user.language.yandex_lang_code
        trans_msgs = []

        for contact in contacts:
            contact_lang = contact.language.yandex_lang_code
            if lang_code == contact_lang:
                trans_msgs.append([user_message])
            else:
                trans_msgs.append(yandex.translate_message(user_message, lang_code, contact_lang))

    return render_template("translated_text.html", trans_msgs=trans_msgs)

    # TODO: create Language controller that will have all above stuff, 
    # calling translate_message() function from that controller in this route 

@app.route("/users/<int:user_id>/send_text/send", methods=["POST"])
def send_text():
    """Send text via Twilio"""

    message = request.form.get("text")

    new_message = Message(message=message)

    #yandex to translate
    #twilio to send


# else:
#             new_message = Message(message=user_message,
#                                   user_id=user[0].user_id,
#                                   )
#             db.session.add(new_rating)

#         db.session.commit()

#         message = Message.query.get(message_id)
#     db.session.add(new_message)
#     db.session.commit()

    flash("Message was sent.")

#TODO send text POST and POST which will return AJAX response
# @app.route("/users/<int:user_id>/send_text", methods=["POST"])
# def preview_text():
#     """Send text"""



#     # post vars
#     #save message and translated text from API
#     #or save them both
#     #condtions (if preview - returns form) - route/ shows translated page, and edit message
#     #if sent - route to Twilio, confirmation shows up

# # import requests - research for python or via JS,build route and
#     return render_template("message_form.html")


#TODO redirect, confirmation page if text is sent

#"/users/<int:user_id>"/messages - all of their messages GET, pagination or dynamic AJAX look-up
# @app.route("/users/<int:user_id>/messages", messages=["GET"])
# def show_messages():
#     """Show list of messages of a user"""

#     messages = Message.query.order_by('message_id').all()
#     return render_template("message_list.html", messages=messages)


# #TODO pre-view -> same as 111, preview and send buttons, still AJAX, but diff route



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()


    # users messages controller

    # yandex api - take a massege, take an original lang and target lang and figure out what the reponse is

    # messages,py file - handles back-end stuff thay handles messages
