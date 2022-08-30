import os
from twilio.rest import Client
import pandas as pd

def twilio_message_send(inputdf,endpoint):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twil_num = os.environ['TWILIO_NUMBER']
    client = Client(account_sid, auth_token)

    avail = inputdf[inputdf['availabilty'] == 1]
    listavail = avail['pos'].to_list()
    finstring = ('spaces available at positions:', listavail)
    client.messages.create(
                                body=finstring,
                                from_=twil_num,
                                to=endpoint
                            )

