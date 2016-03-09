# LingoChat

LingoChat is a full-stack web application that lets people send and receive text messages with their friends and family in any language. By letting everyone use their own language, LingoChat allows for multilingual conversations. Users can create new contacts or import them from their gmail contacts. A user can preview and edit a translated message prior to sending it to their chosen contacts. If both users have an account in LingoChat, they can chat with each other live in their own languages via websockets. There is also sentiment analysis where each user's messages are broken down into positive, negative and neutral categories. Each user can also see which contacts got the most positive, negative or neutral messages.

LingoChat - Your Channel. Your Chat. Your Language.

# Tech Stack

Python, Flask, PostgreSQL, SQLAlchemy, AngularJS, HTML/CSS, Bootstrap, Javascript, jQuery, AJAX, Chartjs, Pickle, Yandex Translate API, Google Contacts API with OAuth, Twilio API, TextBlob Sentiment API

# Setup

* Clone this repo to your local machine
* Create a virtual environment by running: **virtualenv env**
* Activate your virtualenv: **source bin/env/activate**  
* Run **pip install -r requirements.txt** to install all the dependencies
* Run server **python server.py**

# Required API Keys

* To use translation service, get [Yandex Translate Keys] (https://tech.yandex.com/translate/)
* For Twilio messaging, get a key [here] (https://www.twilio.com/docs/api/rest/sending-messages)
* To access google contact importing, check [Google Contacts API] (https://developers.google.com/google-apps/contacts/v3/)
* Store **all** keys in secret.sh file.
* To get an access to your keys, run **source secret.sh**

#Features

**Configuration Process**

* Once registered, the user can create new contacts or import their Google contacts.
* User's can edit or delete their contacts:
* All CRUD (create, read, update, delete) operations as well as form validations are handled with AngularJS.

**Send & Receive Message**

* With Yandex Translate and Twilio integrations, users are able to send a message to any contact and get a response back in their own language. 

**Caching Messages**

* By caching all translated messages in my db, I first make a call to db to check for the translated text and then to Yandex, limiting the use of API calls and making the response faster.

**LiveChat Feature**

* Registered users can chat real-time with live translation via websockets.

**Sentiment Analysis**

* TextBlob Sentiment API calculates subjectivity and polarity of all sent messages, including non-english ones to show the percentage pf positive, negative and neutral messages as well as indicate which contacts got the most positive, negative or neutral texts. The results are visualized with ChartJS library.

#Author

Malika Nikhmonova is from San Francisco, CA. See her [LinkedIn Profile] (https://www.linkedin.com/in/malika-nikhmonova-31a823a8?trk=hp-identity-name) 
