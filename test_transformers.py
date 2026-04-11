import numpy as np
from PIL import Image
from transformers import pipeline
import time

try:
    print("Loading emotion classification model...")
    t1 = time.time()
    emotion_classifier = pipeline("image-classification", model="dima806/facial_emotions_image_detection")
    t2 = time.time()
    print(f"Model loaded in {t2-t1:.2f} seconds")
    
    # Create a blank image to test
    img = Image.new('RGB', (224, 224), color = 'red')
    res = emotion_classifier(img)
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()
