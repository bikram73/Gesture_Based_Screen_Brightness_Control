import cv2 
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
from math import hypot
import screen_brightness_control as sbc
import numpy as np 
from flask import Flask, render_template, Response

# Download hand landmarker model if not exists
MODEL_PATH = 'hand_landmarker.task'
if not os.path.exists(MODEL_PATH):
    print("Downloading hand landmarker model...")
    url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task'
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Model downloaded successfully!")

app = Flask(__name__)

# Create hand landmarker with new API
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    running_mode=vision.RunningMode.IMAGE
)
detector = vision.HandLandmarker.create_from_options(options)

mpDraw = vision.drawing_utils
HandLandmarksConnections = vision.HandLandmarksConnections

def generate_frames():
    cap = cv2.VideoCapture(0)
    try:
        try:
            b_val = sbc.get_brightness()
            current_brightness = b_val[0] if isinstance(b_val, list) else b_val
        except Exception:
            current_brightness = 50

        prev_center = None
        still_frames = 0
        movement_pause = False
            
        while True:
            success,img = cap.read()
            if not success:
                continue
            
            # Mirror the image horizontally for a more natural feel
            img = cv2.flip(img, 1)
            
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

                # Pause only when hand movement stops for a short period.
                center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
                if prev_center is not None:
                    move_dist = hypot(center_x - prev_center[0], center_y - prev_center[1])
                    if move_dist < 2.0:
                        still_frames += 1
                    else:
                        still_frames = 0
                prev_center = (center_x, center_y)
                movement_pause = still_frames >= 8

                if movement_pause:
                    cv2.putText(img, 'Status: PAUSED', (20, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    length = hypot(x2-x1,y2-y1)

                    # Tuned range so normal hand motion can reach full 0-100%
                    target_brightness = np.interp(length, [20, 130], [0, 100])
                    
                    # Smooth the brightness change to prevent jittering (20% towards target per frame)
                    current_brightness += (target_brightness - current_brightness) * 0.2

                    # Allow exact endpoints instead of stalling at low/high values.
                    if target_brightness >= 99 and current_brightness >= 98.5:
                        current_brightness = 100
                    elif target_brightness <= 1 and current_brightness <= 1.5:
                        current_brightness = 0

                    current_brightness = float(np.clip(current_brightness, 0, 100))
                    sbc.set_brightness(int(round(current_brightness)))
            else:
                prev_center = None
                still_frames = 0
                movement_pause = False
                
            # Calculate dynamic color (BGR format: from Red to Green)
            color_r = int(np.interp(current_brightness, [0, 100], [255, 0]))
            color_g = int(np.interp(current_brightness, [0, 100], [0, 255]))
            bar_color = (0, color_g, color_r)

            # Display brightness text overlay
            cv2.putText(img, f'Brightness: {int(current_brightness)}%', (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, bar_color, 2, cv2.LINE_AA)

            # Draw brightness visual bar
            bar_y = int(np.interp(current_brightness, [0, 100], [400, 150]))
            cv2.rectangle(img, (20, 150), (50, 400), bar_color, 3) # Outer outline
            cv2.rectangle(img, (20, bar_y), (50, 400), bar_color, cv2.FILLED) # Filled bar

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/app')
def app_page():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Starting web server at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)