# ✋ Gesture-Based Screen Brightness Control

Welcome to the **Gesture Brightness Control** web application! This project utilizes computer vision to track your hand gestures in real-time and dynamically adjust your computer's screen brightness without ever touching your mouse or keyboard.

## ✨ Features

- **🤏 Touchless Brightness Control:** Adjust your screen brightness smoothly by pinching your index finger and thumb together.
- **🛑 Pause Mode:** Open your entire hand (like a stop sign) to temporarily pause brightness calculations and lock your current brightness in place.
- **🤖 Real-time AI Tracking:** Powered by Google's **MediaPipe** and **OpenCV** for highly accurate, fast hand landmark detection.
- **🌐 Beautiful Web Interface:** Fully integrated into a modern, responsive **Flask** web application with a custom camera permission modal.
- **🎨 Visual Feedback:** Features a dynamic on-screen bar that changes color (from red to green) and tracks your brightness percentage smoothly using an Exponential Moving Average algorithm to prevent jitter.

## 📁 File Structure

```text
Brightness_Control_With_Hand_Detection_OpenCV/
│
├── main.py                  # Core Flask backend and OpenCV/MediaPipe logic
├── requirements.txt         # Required Python dependencies
├── hand_landmarker.task     # MediaPipe ML model (Auto-downloads if missing)
│
├── static/
│   └── style.css            # Custom CSS for the web UI styling and responsive design
│
└── templates/
    ├── home.html            # Landing page with project details and features
    └── index.html           # Main web application interface and camera feed
```

## 🚀 Installation & Setup

### 1. Prerequisites
Make sure you have Python 3.8+ installed on your system.

### 2. Clone the Repository
Download or clone this project to your local machine.

### 3. Install Dependencies
Open your terminal/command prompt, navigate to the project folder, and run:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the Flask web server by executing:
```bash
python main.py
```

### 5. Open in Browser
Once the server is running, open your web browser and go to:
**`http://127.0.0.1:5000`**

## 🎮 How to Use

1. Click **"Launch Application"** on the home page.
2. Click **"Grant Camera Access"** on the custom modal and choose **"Allow"** when your browser prompts you.
3. Hold your hand up to the camera. **Pinch** your thumb and index finger to change the brightness. **Open** all fingers to pause!