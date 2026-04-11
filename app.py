"""
Weapon Detection System - Core Application
Powered by YOLOv8 and DeepFace behavior analysis.
"""

import os
import json
import base64
import threading
import time
import shutil
import subprocess
import logging
from datetime import datetime

import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.utils import secure_filename
from ultralytics import YOLO

# Local Modules
from emotion_detector import DeepFace
from email_helper import send_weapon_alert

# ── Configuration ────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_security_sentinel_2024')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov', 'mkv', 'wmv'}

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('models', exist_ok=True)

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Constants
USERS_FILE = 'users.json'
MODEL_PATH = 'models/best.pt'
GENERAL_MODEL_PATH = 'yolov8s.pt' 

# Detection Constants
RELIABILITY_THRESHOLD = 40
COCO_WEAPON_CLASS_IDS = {34: 'blunt-object', 39: 'improvised-weapon', 43: 'bladed-weapon', 76: 'bladed-weapon'}
COCO_LABEL_REMAP = {
    34: 'blunt-weapon (wood/rod/pipe)',
    39: 'improvised-weapon (bottle/glass)',
    43: 'bladed-weapon (knife/blade/axe)',
    76: 'bladed-weapon (scissors)',
}

# ── Globals (Webcam state) ───────────────────────────────────────────────────

class DetectionState:
    def __init__(self):
        self.camera_active = False
        self.current_frame = None
        self.results = {"weapons": [], "behaviors": []}
        self.lock = threading.Lock()

state = DetectionState()

# ── Utility Functions ────────────────────────────────────────────────────────

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_video_file(filename):
    video_extensions = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in video_extensions

def safe_float_convert(value):
    if hasattr(value, 'item'):
        return float(value.item())
    return float(value)

# ── Model Management ─────────────────────────────────────────────────────────

_models = {'custom': None, 'general': None}

def get_custom_model():
    if _models['custom'] is None:
        if os.path.exists(MODEL_PATH):
            try:
                _models['custom'] = YOLO(MODEL_PATH)
                logger.info(f"Custom model loaded from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load custom model: {e}")
    return _models['custom']

def get_general_model():
    if _models['general'] is None:
        try:
            _models['general'] = YOLO(GENERAL_MODEL_PATH)
            logger.info("General COCO model loaded")
        except Exception as e:
            logger.error(f"Failed to load general model: {e}")
    return _models['general']

# ── Detection Engines ────────────────────────────────────────────────────────

def run_fallback_detection(image_input, conf_threshold=0.25):
    fallback_weapons = []
    annotated = None
    gm = get_general_model()
    if not gm: return [], None

    try:
        results = gm(image_input, conf=conf_threshold, iou=0.4, imgsz=640, verbose=False)
        for result in results:
            if result.boxes:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    if cls in COCO_WEAPON_CLASS_IDS:
                        conf = safe_float_convert(box.conf[0])
                        label = COCO_LABEL_REMAP.get(cls, 'bladed-weapon')
                        fallback_weapons.append({
                            'class': label,
                            'confidence': round(conf * 100, 1)
                        })
            if fallback_weapons and annotated is None:
                annotated = result.plot()
    except Exception as e:
        logger.error(f"Fallback detection error: {e}")
    return fallback_weapons, annotated

def detect_weapons(image_path, behavior_threat_level=0):
    try:
        model = get_custom_model()
        if not model: return [], image_path
    
        conf_threshold = 0.15 if behavior_threat_level > 60 else 0.25
        results = model(image_path, conf=conf_threshold, iou=0.3, imgsz=1024, agnostic_nms=True, augment=True, verbose=False)
        
        weapons = []
        primary_annotated = None
        for result in results:
            if result.boxes:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    conf = safe_float_convert(box.conf[0])
                    class_name = result.names[cls]
                    weapons.append({
                        'class': class_name,
                        'confidence': round(conf * 100, 1)
                    })
            if result.boxes and len(result.boxes) > 0:
                primary_annotated = result.plot()

        # Reliability Check
        max_custom_conf = max([w['confidence'] for w in weapons], default=0)
        custom_reliable = max_custom_conf >= RELIABILITY_THRESHOLD

        fallback_annotated = None
        if not weapons or not custom_reliable:
            fallback_weapons, fallback_annotated = run_fallback_detection(image_path)
            if fallback_weapons:
                max_fallback_conf = max([w['confidence'] for w in fallback_weapons], default=0)
                if max_fallback_conf > max_custom_conf:
                    weapons = fallback_weapons
                    primary_annotated = None
            elif not custom_reliable and weapons:
                weapons = []
                primary_annotated = None

        output_path = image_path.replace('.', '_detected.')
        best_annotated = primary_annotated if primary_annotated is not None else fallback_annotated
        
        if best_annotated is not None:
            cv2.imwrite(output_path, best_annotated)
        else:
            shutil.copy2(image_path, output_path)
            
        return weapons, output_path
    except Exception as e:
        logger.error(f"Weapon detection error: {e}")
        return [], image_path

# ── Behavioral Intelligence ──────────────────────────────────────────────────

def analyze_behavior(image_input):
    """Forensic behavior analysis based on facial biometrics."""
    try:
        result = DeepFace.analyze(image_input, actions=['emotion'], enforce_detection=False)
        if isinstance(result, list): result = result[0]
        
        emotions = result.get('emotion', {})
        fear = emotions.get('fear', 0)
        angry = emotions.get('angry', 0)
        disgust = emotions.get('disgust', 0)
        surprise = emotions.get('surprise', 0)
        neutral = emotions.get('neutral', 0)
        sad = emotions.get('sad', 0)
        happy = emotions.get('happy', 0)
        
        dominant = result.get('dominant_emotion', 'neutral')

        # Threat Matrix
        aggression = angry * 1.6 + disgust * 1.0
        distress = fear * 1.5 + sad * 0.9
        stability = (happy * 2.0 + neutral * 1.5) * (2.0 if happy > 70 else 1.0)
        threat_index = max(0, min(100, (aggression + distress + (surprise * 0.5)) - stability))

        # Classification Tree
        if aggression > 80 and stability < 30:
            label = "Threatening / Extreme Aggression"
            dominant = "hostile"
        elif aggression > 50 and stability < 40:
            label = "Angry / Hostile Behavior"
        elif happy > 60:
            label = "Happy / Stable"
        elif fear > 50:
            label = "Fear / Potential Victim"
        elif sad > 50:
            label = "Crying / Distressed"
        elif threat_index > 50:
            label = "Anxious / Highly Agitated"
        elif threat_index > 15 and fear < 20:
            label = "Stable / Normal"
        else:
            label = "Stable / Clear"

        confidence = max(threat_index, fear * 0.8) if (threat_index > 15 or fear > 30) else 0

        return [{
            'behavior': label,
            'confidence': round(safe_float_convert(confidence), 1),
            'dominant_emotion': dominant
        }]
    except Exception as e:
        logger.error(f"Behavior analysis error: {e}")
        return []

# ── Video Processing ──────────────────────────────────────────────────────────

def process_video(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        temp_output = video_path.replace('.', '_temp.').rsplit('.', 1)[0] + '.mp4'
        output_path = video_path.replace('.', '_detected.').rsplit('.', 1)[0] + '.mp4'
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))
        
        all_weapons = []
        all_behaviors = []
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
                
            frame_idx += 1
            if frame_idx % 30 == 0:
                behaviors = analyze_behavior(frame)
                threat = behaviors[0]['confidence'] if behaviors else 0
                all_behaviors.extend(behaviors)
                
                # Mocking detection for frame to save time/resources
                res_frame, weapons = detect_weapons_frame(frame, threat)
                all_weapons.extend(weapons)
                out.write(res_frame)
            else:
                out.write(frame)
        
        cap.release()
        out.release()
        
        # Convert to web-friendly format via FFmpeg
        convert_to_web_format(temp_output, output_path)
        
        # Aggregate results
        unique_weapons = list({(w['class'], w['confidence']): w for w in all_weapons}.values())
        unique_behaviors = list({(b['behavior']): b for b in all_behaviors}.values())
        
        return unique_weapons, unique_behaviors, output_path
        
    except Exception as e:
        logger.error(f"Video processor failed: {e}")
        return [], [], video_path

def convert_to_web_format(input_p, output_p):
    try:
        cmd = ['ffmpeg', '-i', input_p, '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', '-y', output_p]
        subprocess.run(cmd, capture_output=True, check=True)
        if os.path.exists(input_p): os.remove(input_p)
    except Exception as e:
        logger.warning(f"FFmpeg conversion failed: {e}")
        if os.path.exists(input_p): os.rename(input_p, output_p)

def detect_weapons_frame(frame, behavior_threat=0):
    model = get_custom_model()
    if not model: return frame, []
    conf = 0.15 if behavior_threat > 60 else 0.25
    results = model(frame, conf=conf, imgsz=640, verbose=False)
    weapons = []
    annotated = frame
    for result in results:
        if result.boxes:
            for box in result.boxes:
                weapons.append({'class': result.names[int(box.cls[0])], 'confidence': round(safe_float_convert(box.conf[0]) * 100, 1)})
            annotated = result.plot()
    return annotated, weapons

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return redirect(url_for('detection' if 'username' in session else 'login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        user = next(((u, d) for u, d in users.items() if d['email'] == email), None)
        
        if user and user[1]['password'] == password:
            session['username'] = user[0]
            session['email'] = user[1]['email']
            flash('Session authenticated.', 'success')
            return redirect(url_for('detection'))
        flash('Authentication failed.', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u, e, p, cp = request.form.get('username'), request.form.get('email'), request.form.get('password'), request.form.get('confirm_password')
        if p != cp:
            flash('Password mismatch.', 'error')
        else:
            users = load_users()
            if u in users: flash('Username taken.', 'error')
            else:
                users[u] = {'email': e, 'password': p, 'created_at': str(datetime.now())}
                save_users(users)
                flash('Profile created.', 'success')
                return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/detection')
def detection():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('detection.html', username=session['username'])

@app.route('/detect', methods=['POST'])
def detect():
    if 'username' not in session: return redirect(url_for('login'))
    
    input_type = request.form.get('input_type')
    if input_type == 'webcam':
        with state.lock:
            weapons, behaviors = state.results["weapons"], state.results["behaviors"]
            res_img = f"webcam_{int(time.time())}.jpg"
            if state.current_frame is not None:
                cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], res_img), state.current_frame)
            else: res_img = "error.jpg"
    else:
        file = request.files.get('file')
        if not file or file.filename == '' or not allowed_file(file.filename):
            flash('Invalid intel source.', 'error')
            return redirect(url_for('detection'))
        
        fname = secure_filename(f"{int(time.time())}_{file.filename}")
        fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
        file.save(fpath)
        
        if is_video_file(fname):
            weapons, behaviors, out_path = process_video(fpath)
            res_img = os.path.basename(out_path)
        else:
            behaviors = analyze_behavior(fpath)
            threat = behaviors[0]['confidence'] if behaviors else 0
            weapons, out_path = detect_weapons(fpath, threat)
            res_img = os.path.basename(out_path)

    # Threat Assessment Logic
    threat_level = "ALL CLEAR"
    if weapons and behaviors:
        # Contextual override: Any active motion + weapon = Armed Aggressor
        for b in behaviors:
            if b['behavior'] not in ["Fear / Potential Victim"]:
                b['behavior'] = "Aggressive / Hostile (Armed)"
                b['confidence'] = max(b['confidence'], 90)
        threat_level = "CRITICAL: ARMED ASSAULT"
    elif weapons: threat_level = "HIGH ALERT: WEAPON DETECTED"
    elif behaviors:
        if any(b['confidence'] > 70 for b in behaviors): threat_level = "ELEVATED: SUSPICIOUS BEHAVIOR"

    # Alert System
    email_sent, email_msg = False, "No weapons detected"
    if weapons:
        email_sent, email_msg = send_weapon_alert(session['username'], weapons, behaviors, os.path.join(app.config['UPLOAD_FOLDER'], res_img), threat_level)

    return render_template('results.html', weapons_detected=weapons, behaviors_detected=behaviors, result_image=res_img, email_sent=email_sent, email_message=email_msg, input_type=input_type, threat_level=threat_level)

# ── Webcam Feed (Streaming) ───────────────────────────────────────────────────

@app.route('/start_camera')
def start_camera():
    state.camera_active = True
    return jsonify({"status": "success"})

@app.route('/stop_camera')
def stop_camera():
    state.camera_active = False
    return jsonify({"status": "success"})

@app.route('/video_feed')
def video_feed():
    def gen():
        cap = cv2.VideoCapture(0)
        fc = 0
        while state.camera_active:
            ok, frame = cap.read()
            if not ok: break
            with state.lock: state.current_frame = frame.copy()
            fc += 1
            if fc % 15 == 0:
                bh = analyze_behavior(frame)
                th = bh[0]['confidence'] if bh else 0
                ann, wp = detect_weapons_frame(frame, th)
                with state.lock: state.results = {"weapons": wp, "behaviors": bh}
                disp = ann
            else: disp = frame
            
            _, buf = cv2.imencode('.jpg', disp)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')
        cap.release()
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_detection_status')
def get_status():
    with state.lock: return jsonify(state.results)

@app.route('/logout')
def logout():
    state.camera_active = False
    session.clear()
    return redirect(url_for('login'))

@app.route('/serve_video/<filename>')
def serve_video(filename):
    # Professional range-aware video serving
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    size = os.path.getsize(path)
    def generate():
        with open(path, 'rb') as f:
            while True:
                data = f.read(8192)
                if not data: break
                yield data
    return Response(generate(), mimetype='video/mp4', headers={'Content-Length': str(size), 'Accept-Ranges': 'bytes'})

if __name__ == '__main__':
    logger.info("SecuritySentinel initializing...")
    app.run(host='0.0.0.0', port=5000, debug=True)