import twilio.twiml
import os
from twilio.rest import TwilioRestClient

 
# Your Account Sid and Auth Token from twilio.com/user/account

TWILIO_ACCOUNT_SID=os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN=os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER=str(os.environ.get("TWILIO_NUMBER"))

client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_message(user_message, contact_phone):
    """Send a translated text message to contacts"""
    # twilio.rest.TwilioRestClient
    
    message = client.messages.create(body=user_message,
                                     to='+1' + contact_phone,
                                     from_=TWILIO_NUMBER
                                    )

