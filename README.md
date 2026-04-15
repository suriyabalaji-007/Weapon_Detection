# 🛡️ SecuritySentinel — AI-Powered Weapon & Threat Detection System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-0052CC?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/DeepFace-Biometric_AI-FF6F00?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/TensorFlow-2.20-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
</p>

> **SecuritySentinel** is a real-time, neural-network-driven threat intelligence platform that combines weapon detection with behavioral biometric analysis. It enables security operators to analyze live webcam feeds, uploaded images, and video footage to identify armed threats and assess suspect behavior — dispatching automated forensic alerts when critical conditions are met.

---

## 📸 Overview

The system integrates two independent AI pipelines:

1. **Weapon Detection** — A custom-trained YOLOv8 model identifies firearms, bladed weapons, blunt objects, and improvised weapons with high-confidence bounding box annotations. A COCO-class fallback engine activates automatically when the primary model returns low-confidence detections.

2. **Behavioral Intelligence** — A DeepFace-powered facial emotion recognition module analyzes suspects' emotional states (anger, fear, aggression, distress) and computes a composite **Threat Index Score**. This score dynamically lowers the weapon detection sensitivity threshold when hostile behavior is detected.

When both a weapon **and** hostile behavior are detected together, the system instantly escalates to a **CRITICAL: ARMED ASSAULT** alert and dispatches an automated forensic report via SMTP email to registered security personnel.

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| 🔫 **Multi-class Weapon Detection** | Identifies bladed weapons, blunt objects, firearms, and improvised weapons using a fine-tuned YOLOv8 model |
| 🧠 **Behavioral Threat Analysis** | Analyses facial emotions to generate a live Threat Index, classifying suspects from "Stable/Clear" to "Extreme Aggression" |
| 🎥 **Live Webcam Streaming** | Real-time MJPEG camera feed with detection overlays rendered at every 15th frame |
| 📹 **Video File Analysis** | Processes uploaded video files frame-by-frame (every 30th frame) and outputs an annotated MP4 via FFmpeg |
| 🖼️ **Image Analysis** | Static image uploads analyzed for both weapon presence and emotional state |
| 📧 **Automated Email Alerts** | HTML-formatted forensic alert emails with annotated image attachments dispatched via encrypted SMTP (TLS) |
| 🔐 **User Authentication** | Session-based login/signup system with JSON-backed user store |
| ⚡ **Dual-Model Fallback** | Seamlessly falls back to COCO-class detection (YOLOv8s) when the custom model confidence is insufficient |
| 🎨 **Glassmorphism UI** | Premium dark-mode interface with glassmorphism design, smooth animations, and responsive layouts |

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.9+, Flask 3.1 |
| **Object Detection** | Ultralytics YOLOv8 (Custom `best.pt` + `yolov8s.pt` COCO fallback) |
| **Behavioral Analysis** | DeepFace 0.0.95 (MTCNN face detection + TF/Keras emotion classifier) |
| **Computer Vision** | OpenCV 4.x |
| **Deep Learning** | TensorFlow 2.20, Keras 3.12, PyTorch 2.9 |
| **Video Processing** | FFmpeg (H.264 / `libx264` re-encoding for browser compatibility) |
| **Email Dispatch** | Python `smtplib` with STARTTLS encryption (Gmail SMTP) |
| **Frontend** | HTML5, Vanilla CSS (Glassmorphism Design System) |

---

## 📁 Project Structure

```
weapon1/
├── app.py                    # Core Flask application — routes, detection engine, streaming
├── emotion_detector.py       # DeepFace wrapper for behavioral analysis
├── email_helper.py           # Encrypted SMTP alert dispatcher
├── train_model.py            # YOLOv8 custom-training script
├── deepface_mock.py          # Mock module for offline/test runs
│
├── models/
│   └── best.pt               # Custom-trained YOLOv8 weapon detection model
├── yolov8s.pt                # General COCO YOLOv8s fallback model
│
├── templates/
│   ├── login.html            # Authentication page
│   ├── signup.html           # Registration page
│   ├── detection.html        # Main operator dashboard (image/video/webcam input)
│   └── results.html          # Forensic results & threat assessment report
│
├── static/
│   ├── css/style.css         # Glassmorphism design system
│   └── uploads/              # Uploaded media & annotated output files
│
├── dataset/                  # Training dataset (images + labels)
├── runs/                     # YOLOv8 training run artifacts
├── requirements_updated.txt  # Pinned dependency list
├── run_project.bat           # Windows quick-launch script
└── run_project.ps1           # PowerShell quick-launch script
```

---

## ⚙️ Threat Classification Logic

The system applies a multi-factor **Threat Matrix** to classify behavioral states:

```
Aggression Score  = angry × 1.6 + disgust × 1.0
Distress Score    = fear × 1.5 + sad × 0.9
Stability Score   = (happy × 2.0 + neutral × 1.5) × [2.0 if happy > 70]
Threat Index      = clamp(0–100, Aggression + Distress + Surprise×0.5 − Stability)
```

**Threat Levels (ascending):**

| Label | Condition |
|---|---|
| ✅ Stable / Clear | Default baseline |
| 🟡 Stable / Normal | Threat Index 15–50, low fear |
| 🟠 Anxious / Highly Agitated | Threat Index > 50 |
| 🔴 Angry / Hostile Behavior | Aggression > 50, Stability < 40 |
| 🚨 Threatening / Extreme Aggression | Aggression > 80, Stability < 30 |
| 💀 Aggressive / Hostile (Armed) | Weapon **+** hostile behavior detected simultaneously |

When `Threat Index > 60`, weapon detection confidence threshold is **automatically lowered from 25% → 15%**, increasing sensitivity to catch even partially-visible weapons.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to system `PATH`
- A webcam (optional, for live feed)

### 1. Clone & Set Up Environment

```powershell
git clone https://github.com/your-username/security-sentinel.git
cd security-sentinel/weapon1

python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements_updated.txt
```

> ⚠️ The full dependency stack includes TensorFlow, PyTorch, and Ultralytics. Installation may take several minutes and requires ~6 GB of disk space.

### 3. Add Your Model

Place your trained YOLOv8 model at:
```
models/best.pt
```
The system will automatically fall back to `yolov8s.pt` (COCO) if no custom model is present.

### 4. Launch the Server

```powershell
python app.py
```

Or use the provided quick-launch scripts:
```powershell
# PowerShell
.\run_project.ps1

# Command Prompt / Batch
run_project.bat
```

Access the dashboard at: **`http://127.0.0.1:5000`**

---

## 🔐 Default Test Credentials

| Role | Email | Password |
|---|---|---|
| **Lead Operator** | `test@gmail.com` | `123456` |

> Create additional accounts via the `/signup` route.

---

## 📧 Email Alert Configuration

The alert system uses environment variables for secure credential management. Set these before running:

```powershell
$env:SENTINEL_EMAIL_USER = "your-sender@gmail.com"
$env:SENTINEL_EMAIL_PASS  = "your-app-password"      # Gmail App Password (not your main password)
$env:SENTINEL_ALERT_TARGET = "security-team@org.com"
```

> Gmail requires an **App Password** (2FA must be enabled). Generate one at: [Google Account → Security → App Passwords](https://myaccount.google.com/apppasswords)

---

## 🧠 Model Training

To train or retrain the custom weapon detection model:

```powershell
python train_model.py
```

Dataset should follow YOLOv8 format (images + `.txt` label files) placed under `dataset/`.  
Training artifacts and weights are saved under `runs/`.

---

## 🔒 Security Notes

- Passwords are currently stored in plain text in `users.json`. For production use, replace with hashed storage (e.g., `bcrypt`).
- Email credentials should always be provided via environment variables, never hardcoded.
- This system is intended for **controlled security research and authorized deployment only**.

---

## 📄 License

This project is intended for academic and security research purposes.  
Unauthorized use for surveillance without consent may violate applicable laws.

---

*Built with ❤️ using Ultralytics YOLOv8, DeepFace, and Flask.*
