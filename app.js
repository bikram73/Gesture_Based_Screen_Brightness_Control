import { FilesetResolver, HandLandmarker } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14";

const grantBtn = document.getElementById("grant-btn");
const modal = document.getElementById("camera-modal");
const toggleBtn = document.getElementById("toggle-btn");
const statusEl = document.getElementById("status");
const valueEl = document.getElementById("value");
const meterEl = document.getElementById("meter");
const videoShell = document.getElementById("video-shell");

const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");

let stream = null;
let running = false;
let handLandmarker = null;
let animationId = null;
let currentBrightness = 50;

function setStatus(text) {
  statusEl.textContent = `Status: ${text}`;
}

function updateVisualBrightness(value) {
  const clamped = Math.max(0, Math.min(100, value));
  currentBrightness = clamped;
  valueEl.textContent = `Brightness: ${Math.round(clamped)}%`;
  meterEl.style.height = `${clamped}%`;
  videoShell.style.filter = `brightness(${0.45 + clamped / 100})`;
}

function dist(p1, p2) {
  const dx = p1.x - p2.x;
  const dy = p1.y - p2.y;
  return Math.sqrt(dx * dx + dy * dy);
}

function map(value, inMin, inMax, outMin, outMax) {
  const t = (value - inMin) / (inMax - inMin);
  const n = Math.max(0, Math.min(1, t));
  return outMin + n * (outMax - outMin);
}

function isOpenHand(landmarks) {
  const tips = [8, 12, 16, 20];
  const pips = [6, 10, 14, 18];
  let up = 0;
  for (let i = 0; i < tips.length; i += 1) {
    if (landmarks[tips[i]].y < landmarks[pips[i]].y) up += 1;
  }
  return up === 4;
}

function drawLandmarks(landmarks) {
  ctx.fillStyle = "#48d1ff";
  for (const lm of landmarks) {
    const x = lm.x * canvas.width;
    const y = lm.y * canvas.height;
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();
  }

  const thumb = landmarks[4];
  const index = landmarks[8];
  if (thumb && index) {
    ctx.strokeStyle = "#3dff9b";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(thumb.x * canvas.width, thumb.y * canvas.height);
    ctx.lineTo(index.x * canvas.width, index.y * canvas.height);
    ctx.stroke();
  }
}

async function loadModel() {
  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm"
  );

  handLandmarker = await HandLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath:
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    },
    numHands: 1,
    runningMode: "VIDEO"
  });
}

function renderLoop() {
  if (!running) return;

  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const now = performance.now();
  const result = handLandmarker.detectForVideo(video, now);

  if (result.landmarks && result.landmarks.length > 0) {
    const landmarks = result.landmarks[0];
    drawLandmarks(landmarks);

    if (isOpenHand(landmarks)) {
      setStatus("PAUSED");
    } else {
      const d = dist(landmarks[4], landmarks[8]);
      const target = map(d, 0.03, 0.35, 0, 100);
      const smoothed = currentBrightness + (target - currentBrightness) * 0.2;
      updateVisualBrightness(smoothed);
      setStatus("TRACKING");
    }
  } else {
    setStatus("NO HAND");
  }

  animationId = requestAnimationFrame(renderLoop);
}

async function startCamera() {
  if (!handLandmarker) {
    await loadModel();
  }

  stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
    audio: false
  });

  video.srcObject = stream;
  await video.play();

  running = true;
  toggleBtn.disabled = false;
  toggleBtn.textContent = "Stop Camera";
  toggleBtn.classList.remove("btn-off");
  setStatus("TRACKING");

  renderLoop();
}

function stopCamera() {
  running = false;
  if (animationId) cancelAnimationFrame(animationId);
  animationId = null;

  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }
  stream = null;

  video.srcObject = null;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  toggleBtn.textContent = "Start Camera";
  toggleBtn.classList.add("btn-off");
  setStatus("STOPPED");
}

grantBtn.addEventListener("click", async () => {
  try {
    grantBtn.disabled = true;
    await startCamera();
    modal.style.display = "none";
  } catch (error) {
    setStatus("CAMERA BLOCKED");
    grantBtn.disabled = false;
    alert("Camera permission is required to use this app.");
  }
});

toggleBtn.addEventListener("click", async () => {
  if (running) {
    stopCamera();
  } else {
    try {
      await startCamera();
    } catch (error) {
      setStatus("CAMERA BLOCKED");
      alert("Could not start camera.");
    }
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key.toLowerCase() === "q") {
    stopCamera();
  }
});

updateVisualBrightness(50);
setStatus("IDLE");
