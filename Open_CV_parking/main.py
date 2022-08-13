import cv2
import pickle
import numpy as np 
import datetime

width,height = 175,100
log = []
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
            available = 0
            color = (0,255,0)
            logger = F'pos: {posList.index(pos)}, time: {timestamp} , available: {available}'
            print(logger)
            log.append(logger)
            spacecounter +=1
        else: 
            available = 1
            logger = F'pos: {posList.index(pos)},time: {timestamp} , available: {available}'
            print(logger)
            log.append(logger)
            color = (0,0,255)
        cv2.rectangle(img,pos,(pos[0]+width,pos[1]+height),color,2)
    cv2.putText(img,f"Spaces Available: {spacecounter}",(100,100), cv2.FONT_HERSHEY_PLAIN, 2,(255,255,255))
with open('carparkpos','rb') as f:
        posList = pickle.load(f)

vid = cv2.VideoCapture(1)
while True:
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

    # for pos in posList:
    #     cv2.rectangle(img,pos,(pos[0]+width,pos[1]+height),(255,0,255),2)

    cv2.imshow("image",img)
    # cv2.imshow("imageb",imgblur)
    # cv2.imshow("imag",imgthreshold)
    # cv2.imshow("im",imgmed)
    # cv2.imshow("final", imagedial)
    cv2.waitKey(100)