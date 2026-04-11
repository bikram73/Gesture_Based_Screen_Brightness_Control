import cv2 
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
from math import hypot
import screen_brightness_control as sbc
import numpy as np 

# Download hand landmarker model if not exists
MODEL_PATH = 'hand_landmarker.task'
if not os.path.exists(MODEL_PATH):
    print("Downloading hand landmarker model...")
    url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task'
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Model downloaded successfully!")

cap = cv2.VideoCapture(0)

# Create hand landmarker with new API
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    running_mode=vision.RunningMode.IMAGE
)
detector = vision.HandLandmarker.create_from_options(options)

mpDraw = vision.drawing_utils
HandLandmarksConnections = vision.HandLandmarksConnections

print("Press 'q' to close the camera and exit...")

while True:
    success,img = cap.read()
    if not success:
        continue
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    
    # Convert to MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
    results = detector.detect(mp_image)

    lmList = []
    if results.hand_landmarks:
        for hand_index, handlandmark in enumerate(results.hand_landmarks):
            for id,lm in enumerate(handlandmark):
                h,w,_ = img.shape
                cx,cy = int(lm.x*w),int(lm.y*h)
                lmList.append([id,cx,cy]) 
            # Draw landmarks on image
            mpDraw.draw_landmarks(
                img, 
                handlandmark, 
                HandLandmarksConnections.HAND_CONNECTIONS if hasattr(HandLandmarksConnections, 'HAND_CONNECTIONS') else None
            )
    
    if lmList != []:
        x1,y1 = lmList[4][1],lmList[4][2]
        x2,y2 = lmList[8][1],lmList[8][2]

        cv2.circle(img,(x1,y1),4,(255,0,0),cv2.FILLED)
        cv2.circle(img,(x2,y2),4,(255,0,0),cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255,0,0),3)

        length = hypot(x2-x1,y2-y1)

        bright = np.interp(length,[15,220],[0,100])
        print(bright,length)
        sbc.set_brightness(int(bright))
        
        # Hand range 15 - 220
        # Brightness range 0 - 100

    cv2.imshow('Image',img)
    if cv2.waitKey(1) & 0xff==ord('q'):
        print("Closing camera...")
        break

# Release resources when camera is closed
cap.release()
cv2.destroyAllWindows()
