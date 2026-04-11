"""
SecuritySentinel Behavioral Intelligence Module
High-fidelity emotion classification using PyTorch transformer models.
"""

import logging
import numpy as np
import cv2
from PIL import Image

try:
    from transformers import pipeline
    # Load advanced facial emotion model from HuggingFace
    # Model ID: dima806/facial_emotions_image_detection
    emotion_classifier = pipeline(
        "image-classification", 
        model="dima806/facial_emotions_image_detection",
        device=-1 # Set to 0 if CUDA is available
    )
    logging.info("Neural emotion classifier initialized (Transformer/PyTorch)")
except ImportError:
    emotion_classifier = None
    logging.warning("Transformers library missing. Behavioral intelligence will be disabled.")

class BehavioralIntelligence:
    """Forensic behavioral analysis system."""
    
    @staticmethod
    def analyze(image_data, *args, **kwargs):
        """Analyze facial biometrics to extract emotional states."""
        if not emotion_classifier:
            return {'dominant_emotion': 'neutral', 'emotion': {'neutral': 100.0}}

        try:
            # Source Resolution
            if isinstance(image_data, str):
                # Load from path
                image = Image.open(image_data).convert('RGB')
            elif isinstance(image_data, np.ndarray):
                # Load from CV2 frame
                rgb_frame = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(rgb_frame)
            else:
                image = Image.fromarray(image_data)
            
            # Semantic Processing
            raw_results = emotion_classifier(image)
            
            # Normalization
            emotions = {r['label'].lower(): r['score'] * 100.0 for r in raw_results}
            
            # Integrity Check (Ensure DeepFace compatibility keys)
            standard_keys = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
            for k in standard_keys:
                if k not in emotions: emotions[k] = 0.0
                    
            dominant = max(emotions, key=emotions.get)
            
            return {
                'dominant_emotion': dominant,
                'emotion': emotions
            }
            
        except Exception as e:
            logging.error(f"Intelligence Processing Failure: {e}")
            return {'dominant_emotion': 'neutral', 'emotion': {'neutral': 100.0}}

# Singleton Instance
DeepFace = BehavioralIntelligence()
