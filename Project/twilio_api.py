import os
from twilio.rest import TwilioRestClient
 
# Your Account Sid and Auth Token from twilio.com/user/account

client = TwilioRestClient(
    os.environ['ACCOUNT_SID'],
    os.environ['AUTH_TOKEN']
    )

 
message = client.messages.get(body="Jenny please?! I love you <3",
    to="+16267107380",    # Replace with your phone number
    from_="+16262437344") # Replace with your Twilio number

print message.sid