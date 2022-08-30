from Twilio_service_class import twilio_message_send
import pandas as pd
import os
basedir = 'C:/Users/Dylan/Documents/GitHub/finalized_projects/Open_CV_parking/Logs/'
checker = pd.read_csv(os.path.join(basedir,'log_2022-08-15_alt.csv')).tail(3)
try:
    twilio_message_send(checker)
except: 
    print('ope')