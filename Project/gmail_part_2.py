import atom.http_core
import pickle
import gdata.contacts.client


token = pickle.load(open('token' + str(user_id) + '.p', 'rb'))

client = gdata.contacts.client.ContactsClient(source='appname')

client = token.authorize(client)


def get_contacts(flask_session):
    """Lists names of user's contacts"""

    feed = client.GetContacts()
    for i, entry in enumerate(feed.entry):
       print entry.name 


