"""
SecuritySentinel Dispatch Module
Encrypted SMTP transmission for emergency threat alerts.
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

def send_weapon_alert(username, weapons_detected, behaviors_detected, image_path, threat_level):
    """Dispatches a high-priority forensic alert via SMTP."""
    
    # Configuration Retrieval (Fallback to provide immediate functionality)
    sender_email = os.environ.get('SENTINEL_EMAIL_USER', 'ayushtiwari.creatorslab@gmail.com')
    sender_password = os.environ.get('SENTINEL_EMAIL_PASS', 'tecx bcym vxdz dtni')
    recipient_email = os.environ.get('SENTINEL_ALERT_TARGET', 'suriyabalaji373@gmail.com')
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    timestamp_full = datetime.now().strftime('%Y-%m-%d | %H:%M:%S')
    
    # Narrative Construction
    weapon_summary = "".join([f"<li><b>{w['class'].upper()}</b> ({w['confidence']}%)</li>" for w in weapons_detected])
    behavior_summary = "".join([f"<li>{b['behavior']} ({b['confidence']}%)</li>" for b in behaviors_detected]) \
                      if behaviors_detected else "<li>No biometric signatures identified.</li>"
    
    # Visual Branding
    accent_color = "#ef4444" if "CRITICAL" in threat_level else "#f59e0b" if "ALERT" in threat_level else "#3b82f6"
    
    html_content = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
        <div style="background-color: {accent_color}; color: white; padding: 30px; text-align: center;">
            <p style="text-transform: uppercase; letter-spacing: 0.2em; font-size: 10px; font-weight: 800; margin-bottom: 8px; opacity: 0.8;">SecuritySentinel Protocol</p>
            <h1 style="margin: 0; font-size: 24px; font-weight: 900;">THREAT DETECTION ALERT</h1>
        </div>
        <div style="padding: 40px; background-color: white;">
            <div style="background-color: #f8fafc; border-left: 4px solid {accent_color}; padding: 20px; margin-bottom: 30px;">
                <p style="margin: 0; font-size: 12px; font-weight: 800; color: #64748b; text-transform: uppercase;">Assessment</p>
                <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 900; color: {accent_color};">{threat_level}</p>
            </div>
            
            <div style="display: grid; grid-template-cols: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div>
                    <p style="margin: 0; font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase;">Operator</p>
                    <p style="margin: 4px 0 0 0; font-size: 14px; font-weight: 600; color: #1e293b;">{username}</p>
                </div>
                <div>
                    <p style="margin: 0; font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase;">Intelligence Time</p>
                    <p style="margin: 4px 0 0 0; font-size: 14px; font-weight: 600; color: #1e293b;">{timestamp_full}</p>
                </div>
            </div>

            <h3 style="font-size: 14px; font-weight: 900; color: #0f172a; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; margin-bottom: 12px;">Identified Targets</h3>
            <ul style="margin: 0; padding-left: 18px; color: #334155; font-size: 13px;">{weapon_summary}</ul>

            <h3 style="font-size: 14px; font-weight: 900; color: #0f172a; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; margin: 24px 0 12px 0;">Biometric Context</h3>
            <ul style="margin: 0; padding-left: 18px; color: #334155; font-size: 13px;">{behavior_summary}</ul>

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #f1f5f9; font-size: 11px; color: #94a3b8; text-align: center;">
                <p>This is an automated forensic intelligence report. Immediate response may be required.</p>
            </div>
        </div>
    </div>
    """

    try:
        msg = MIMEMultipart('related')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"[{threat_level}] Weapon Detected - Forensic Report - {username}"
        
        msg.attach(MIMEText(html_content, 'html'))

        # Media Attachment
        if os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1].lower()
            with open(image_path, 'rb') as f:
                if ext in ['.jpg', '.jpeg', '.png']:
                    part = MIMEImage(f.read())
                else:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(image_path)}"')
                msg.attach(part)

        # Transmission
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        logging.info(f"Forensic alert successfully dispatched to {recipient_email}")
        return True, "Dispatch successful. Security teams notified."
        
    except Exception as e:
        logging.error(f"Dispatch failure: {e}")
        return False, f"Dispatch failed: {str(e)}"