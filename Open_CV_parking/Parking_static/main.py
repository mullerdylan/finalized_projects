import cv2
import pickle
import numpy as np 

width,height = 175,100

def checkspace(imgpro): 
    spacecounter = 0
    for pos in posList:
        x,y = pos

        imgcrop = imgpro[y:y+height, x:x+width]
        cv2.imshow(str(pos), imgcrop)
        count = cv2.countNonZero(imgcrop)
        cv2.putText(img,str(count),(x,y+height-10), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1,(255,255,255))
        if count <1000:
            color = (0,255,0)
            spacecounter +=-1
        else: 
            color = (0,0,255)
        cv2.rectangle(img,pos,(pos[0]+width,pos[1]+height),color,2)
    cv2.putText(img,f"Spaces Available: {spacecounter}",(100,100), cv2.FONT_HERSHEY_PLAIN, 2,(255,255,255))
with open('carparkpos','rb') as f:
        posList = pickle.load(f)

while True:
    img = cv2.imread('parking_im.jpg')
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