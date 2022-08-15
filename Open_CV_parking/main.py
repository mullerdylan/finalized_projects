from asyncio.log import logger
import cv2
import pickle
import numpy as np 
import datetime
import pandas as pd
import os

width,height = 175,100
log = []
parking_position_list = []
timestamp_list = []
availability_list = []
date = datetime.datetime.now().date()

def frame_count(start,end,refresh_rate_min):
    delta = (datetime.datetime.strptime(end,'%H:%M:%S') - datetime.datetime.strptime(start,'%H:%M:%S')).total_seconds()
    frames = round(delta/(refresh_rate_min*60))
    return frames

def checkspace(imgpro): 
    spacecounter = 0
    timestamp = datetime.datetime.now()
    
    for pos in posList:
        x,y = pos
        imgcrop = imgpro[y:y+height, x:x+width]
        cv2.imshow(str(pos), imgcrop)
        count = cv2.countNonZero(imgcrop)
        cv2.putText(img,str(count),(x,y+height-10), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1,(255,255,255))
        if count <1000:
            availability = 0
            color = (0,255,0)
            spacecounter +=1
        else: 
            availability = 1
            color = (0,0,255) 

        parking_position_list.append(posList.index(pos))
        timestamp_list.append(timestamp)
        availability_list.append(availability)

        cv2.rectangle(img,pos,(pos[0]+width,pos[1]+height),color,2)
    cv2.putText(img,f"Spaces Available: {spacecounter}",(100,100), cv2.FONT_HERSHEY_PLAIN, 2,(255,255,255))
with open('carparkpos','rb') as f:
        posList = pickle.load(f)

vid = cv2.VideoCapture(1)
# Function format: (start time, End time, minutes between frame )
inerval_min = .1
max_frame = frame_count('7:00:00','7:01:00',inerval_min)

while len(availability_list)<max_frame*len(posList):
    ret, frame = vid.read()
    img = frame
    imggray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgblur = cv2.GaussianBlur(imggray,(3,3),1) 
    imgthreshold = cv2.adaptiveThreshold(imgblur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY_INV,25,16)
    imgmed = cv2.medianBlur(imgthreshold,5)

    kernel  = np.ones((3,3), np.uint8)
    imagedial = cv2.dilate(imgmed, kernel,iterations = 1)
    checkspace(imagedial)
    
    cv2.imshow("image",img)

    if cv2.waitKey(round(inerval_min*60*1000)) & 0xFF == ord('q'):
        break
# Logic for storing log after program finishes running 
dict = {'pos' : parking_position_list,'timestamps' : timestamp_list , 'availabilty' :availability_list }
df = pd.DataFrame(dict) 
if os.path.exists(F'Logs\log_{date}.csv') ==True:
    df.to_csv(F"Logs\log_{date}_alt.csv", index=False)
else: 
    df.to_csv(F"Logs\log_{date}.csv",index=False)
print(df)