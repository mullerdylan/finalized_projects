import cv2
import pickle


width,height = 175,100
try: 
    with open('carparkpos','rb') as f:
        posList = pickle.load(f)
except:
    posList = []

def mouseclick(events,x,y,flags,params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x,y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i,pos in enumerate(posList):
            x1,y1 = pos
            if x1<x<x1+ width and y1<y<y1+height:
                posList.pop()
    with open('carparkpos','wb') as f:
        pickle.dump(posList,f)

vid = cv2.VideoCapture(1)
while True:
    ret, frame = vid.read()
    for pos in posList:
        cv2.rectangle(frame,pos,(pos[0]+width,pos[1]+height),(255,0,255),2)
    cv2.imshow("image",frame)
    cv2.setMouseCallback("image", mouseclick)
    cv2.waitKey(100)
