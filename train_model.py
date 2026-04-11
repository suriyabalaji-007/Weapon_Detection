import os
from ultralytics import YOLO

def train():
    # Load the Small model (yolov8s.pt) for better accuracy on small objects/perspectives
    # while still being fast enough for real-time
    print("Initializing YOLOv8s Training...")
    model = YOLO('yolov8s.pt')
    
    # Path to your extracted dataset's yaml
    data_yaml = 'datasets/data.yaml'
    
    if not os.path.exists(data_yaml):
        # Check subdirectories
        for root, dirs, files in os.walk('dataset'):
            if 'data.yaml' in files:
                data_yaml = os.path.join(root, 'data.yaml')
                break
    
    if os.path.exists(data_yaml):
        print(f"Dataset found at {data_yaml}. Starting training...")
        # Start training
        # epochs=150: slightly more than original 100 for better convergence
        # imgsz=640: standard training size
        # batch=16: balanced for common hardware
        # augment=True: specifically for CCTV/blurry variations
        results = model.train(
            data=data_yaml, 
            epochs=150, 
            imgsz=640, 
            batch=16, 
            name='weapon_detector_v2',
            patience=20, # Early stopping if no improvement
            augment=True, # Robustness to blur/CCTV
            mosaic=0.5, # Important for small objects
            mixup=0.1 # Background noise robustness
        )
        print("Training complete!")
        print(f"Best model saved to: {results.save_dir}/weights/best.pt")
    else:
        print("CRITICAL ERROR: data.yaml not found in 'dataset' directory.")

if __name__ == "__main__":
    train()
