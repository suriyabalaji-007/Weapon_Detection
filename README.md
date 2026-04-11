# SecuritySentinel v2: Advanced Threat Intelligence System

![Weapon Detection](https://img.shields.io/badge/Security-AI_Powered-blue)
![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-green)
![DeepFace](https://img.shields.io/badge/Behavior-Biometric-orange)

**SecuritySentinel** is a high-performance, neural-network-driven platform designed for automated weapon identification and behavioral threat assessment. By combining state-of-the-art computer vision (YOLOv8) with deep emotional biometrics (Transformers), the system provides real-time situational awareness for security operators.

---

## 🛠️ Technology Stack

*   **Core Engine**: Python 3.9+ with Flask
*   **Object Detection**: Ultralytics YOLOv8 (Custom & COCO Fallback)
*   **Behavioral Analysis**: HuggingFace Transformers (Facial Emotion Recognition)
*   **Frontend**: Tailwind CSS + Glassmorphism Design System
*   **Processing**: FFmpeg for high-speed forensic video analysis
*   **Alerting**: Automated Enrypted SMTP Alerting System

---

## 🚀 Rapid Deployment

### 1. Environment Initialization
Clone the repository and initialize the virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Dependency Resolution
Install the required neural networks and server dependencies:
```powershell
pip install -r requirements_updated.txt
```

### 3. Forensic Configuration (FFmpeg)
Ensure **FFmpeg** is installed and globally accessible via your system's PATH. This is critical for the Multi-Frame Stream processor.
- [Official FFmpeg binaries](https://ffmpeg.org/download.html)

### 4. System Launch
Initialize the SecuritySentinel core:
```powershell
python app.py
```
Access the command center at: `http://127.0.0.1:5000`

---

## 🔐 Intelligence Credentials (Sandbox)

| Identity | Email | Password |
| :--- | :--- | :--- |
| **Lead Operator** | `test@gmail.com` | `123456` |

---

## 🛡️ Key Features

- **Multi-Source Intelligence**: Analyze static frames, uploaded visual streams, or live-node webcam feeds.
- **Dynamic Sensitivity**: Weapon detection thresholds automatically adjust based on the detected behavioral threat level.
- **Forensic Reporting**: Generates high-fidelity visual reports with bounding boxes and biometric logs.
- **Encrypted Dispatch**: Immediate SMTP alerting for critical threat detections.

---
*© 2024 Intelligent Security Systems. Powered by Ultralytics & HuggingFace.*
