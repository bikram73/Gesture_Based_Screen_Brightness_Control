# ✋ Gesture-Based Screen Brightness Control

Welcome to the **Gesture Brightness Control** project. It now uses a split architecture:

- The browser UI performs camera access and hand tracking.
- A local agent running on the user's machine applies the actual system brightness change.

This lets you deploy the UI on Netlify, Vercel, or any static host while still controlling the user's local screen brightness when the companion agent is running.

## ✨ Features

- **🤏 Touchless Brightness Control:** Adjust your screen brightness smoothly by pinching your index finger and thumb together.
- **🛑 Pause Mode:** Open your entire hand (like a stop sign) to temporarily pause brightness calculations and lock your current brightness in place.
- **🤖 Real-time AI Tracking:** Powered by Google's **MediaPipe** and **OpenCV** for highly accurate, fast hand landmark detection.
- **🌐 Deployable Web Interface:** Fully usable as a browser app with a custom camera permission modal.
- **🖥️ System Brightness Agent:** A small local Flask agent receives brightness values and changes the operating system brightness.
- **🎨 Visual Feedback:** Shows a live brightness overlay and hand landmarks directly in the browser.

## 📁 File Structure

```text
Brightness_Control_With_Hand_Detection_OpenCV/
│
├── main.py                  # Legacy local Flask backend and OpenCV/MediaPipe logic
├── local_agent.py           # Local brightness agent that changes OS brightness
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

### 4. Run the Local Brightness Agent
Open a terminal on the user's machine and run:
```bash
python local_agent.py
```

This starts a small API on `http://127.0.0.1:5055` that receives brightness values from the deployed web UI and applies them to the operating system.

### 5. Deploy the Web UI
Deploy the browser app in `templates/` and `static/` to Netlify, Vercel, or another static host.

The deployed page will use the user's webcam and hand tracking in the browser, then send brightness updates to the local agent if it is running.

### 6. Run the Local Flask App (optional legacy mode)
Start the original Flask web server by executing:
```bash
python main.py
```

### 7. Open in Browser
Once the server is running, open your web browser and go to:
**`http://127.0.0.1:5000`**

If you are using the deployed UI, open the hosted site in a browser and keep `local_agent.py` running on the same machine.

## 🎮 How to Use

1. Click **"Launch Application"** on the home page.
2. Click **"Grant Camera Access"** on the custom modal and choose **"Allow"** when your browser prompts you.
3. Hold your hand up to the camera. **Pinch** your thumb and index finger to change the brightness. **Open** all fingers to pause!

## 🔧 Deployment + Local Agent Workflow

1. Open the deployed web UI in the browser.
2. Run `python local_agent.py` on the same machine.
3. Give the browser camera access.
4. Move your hand to control the brightness.

If the local agent is not running, the page still works visually, but it cannot change the OS brightness.