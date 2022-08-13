from time import sleep, time
import cv2
import datetime
import pandas as pd 
import os.path
  
  
# define a video capture object
vid = cv2.VideoCapture(1)
timestamp_list = []
category = []
date = datetime.datetime.now().date()

def frame_count(start,end,refresh_rate_min):
    delta = (datetime.datetime.strptime(end,'%H:%M:%S') - datetime.datetime.strptime(start,'%H:%M:%S')).total_seconds()
    frames = round(delta/(refresh_rate_min*60))
    return frames

# Function format: (start time, End time, minutes between frame )
inerval_min = .1
max_frame = frame_count('7:00:00','7:01:00',inerval_min)

while len(category)<max_frame:
    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    timestamp = datetime.datetime.now()
    # Display the resulting frame
    cv2.imshow('frame', frame)
    timestamp_list.append(timestamp)
    category.append('placeholder')
    print(len(category))
    # inser max frame variable in waitkey to run for entire duration 
    if cv2.waitKey(round(inerval_min*60*1000)) & 0xFF == ord('q'):
        break

dict = {'timestamps' : timestamp_list , 'category' :category }
df = pd.DataFrame(dict) 
if os.path.exists(F'log_{date}.csv') ==True:
    df.to_csv(F"Logs\log_{date}_alt.csv", index=False)
else: 
    df.to_csv(F"Logs\log_{date}.csv",index=False)
print(df)

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()