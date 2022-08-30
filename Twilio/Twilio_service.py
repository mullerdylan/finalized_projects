import os
from tabnanny import check
from twilio.rest import Client
import pandas as pd

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)
basedir = 'C:/Users/Dylan/Documents/GitHub/finalized_projects/Open_CV_parking/Logs/'
# print(os.path.join(basedir,'log_2022-08-15.csv'))

if os.path.exists(os.path.join(basedir,'log_2022-08-15_alt.csv')) == True:
    checker = pd.read_csv(os.path.join(basedir,'log_2022-08-15_alt.csv')).tail(3)
else:
    checker = pd.read_csv(os.path.join(basedir,'log_2022-08-15.csv')).tail(3)

avail = checker[checker['availabilty'] == 1]
listavail = avail['pos'].to_list()
finstring = ('spaces available at position:', listavail)

# message = client.messages.create(
#                               body=finstring,
#                               from_='12184133652',
#                               to='+17127909058'
#                           )

