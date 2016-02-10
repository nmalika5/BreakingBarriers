"""Text Translator."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Language, Contact, Message, MessageLang, MessageContact


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("home.html")


@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form.get("email")
    password = request.form.get("password")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    lang_id = request.form.get("lang")
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
    return redirect("/users/%s" % user.user_id) #TODO send message redirect, link to profile there
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

    for contact in user_contact_list:
        contacts.append((contact.contact_phone, contact.language.lang_name))
    return render_template("user_profile.html", user=user, contacts=contacts)
    # contact = Contacts.query.filter_by(user_id=user_id, contact_id=contact_id).first()

    # if not user_contact_list:
    #     flash("The user has no contacts")
    #     return redirect("/users/<int:user_id>/")
    #vars = usercontroller.sstuff(hjhjgjl)

@app.route("/users/<int:user_id>/add_contact", methods=['GET'])
def show_contact_form(user_id):
    """Show form for contact signup."""

    user = User.query.get(user_id)
    return render_template("contact_add.html")


@app.route("/users/<int:user_id>/add_contact", methods=["POST"])
def add_contact(user_id):
    """Add a contact."""

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    language = request.form["lang"]
    phone = request.form["phone"]

    contact = Contact(contact_first_name=contact_first_name, contact_last_name=contact_last_name,
                    contact_phone=contact_phone, user_id=user_id, lang_id=lang_id)
    
    flash("Contact added.")
    db.session.add(contact)

    db.session.commit()

    return redirect("/users/%s" % user_id)

#     return redirect("/movies/%s" % movie_id)
#     return render_template("user_profile.html", user=user, contacts=contacts)

# @app.route("/users/<int:user_id>/messages", methods=["GET"])
# def message_list(user_id):
#     """Show info about user's messages."""

#     user_message = Message.query.filter_by(user_id=user_id, message_id=message_id.all()

#     return render_template("message_list.html")

#TODO send text route, GET, show form
@app.route("/users/<int:user_id>/send_text", methods=["GET"])
def show_text_form(user_id):
    """Show send message form"""

    existing_message = ""

    return render_template("message_form.html", existing_message=existing_message)

@app.route("/users/<int:user_id>/send_text/preview", methods=["GET"])
def show_preview(user_id):
    """Preview message"""

    # trans_msg = MesgController.translate(Variables)

    trans_msg=""

    #show response from yandex
    return render_template("translated_text.html", trans_msg=trans_msg)

    
'''
    #translate request to yandex 

    function(message, lang)
    contact send it to
    for every contact figure out which langs

    for each of that pair

    yandex call(with this stting from this lang to this lang)

    original lang, target langs and call yandex once
'''

@app.route("/users/<int:user_id>/send_text/preview", methods=["POST"])
def edit_message(user_id):
    """Edit message"""

    user_message = request.form.get("text")

    if user_message:
        user_id = session['user_id']
        user = User.query.filter_by(email=email, password=password).all()

        existing_message = Message.query.filter_by(message_id = message_id, user_id=user[0].user_id).all()

        #if user has message, then edit a message; otherwise, add a new message into Message table

        if existing_message:
            existing_message[0].message_text = user_message

        else:
            new_message = Message(message=user_message,
                                  user_id=user[0].user_id,
                                  )
            db.session.add(new_rating)

        db.session.commit()

        message = Message.query.get(message_id)

        return render_template("message_form.html", message=message, 
                                existing_message=existing_message[0].message_text)


@app.route("/users/<int:user_id>/send_text/send", methods=["POST"])
def send_text():
    """Send text via Twilio"""

    message = request.form.get("text")

    new_message = Message(message=message)

    #yandex to translate
    #twilio to send

    db.session.add(new_message)
    db.session.commit()

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

# @app.route("/movies/<int:movie_id>", methods=['POST'])
# def movie_detail_process(movie_id):
#     """Add/edit a rating."""

#     # Get form variables
#     score = int(request.form["score"])

#     user_id = session.get("user_id")
#     if not user_id:
#         raise Exception("No user logged in.")

#     rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

#     if rating:
#         rating.score = score
#         flash("Rating updated.")

#     else:
#         rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
#         flash("Rating added.")
#         db.session.add(rating)

#     db.session.commit()

#     return redirect("/movies/%s" % movie_id)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()


    # users messages controller

    # yandex api - take a massege, take an original lang and target lang and figure out what the reponse is

    # messages,py file - handles back-end stuff thay handles messages
