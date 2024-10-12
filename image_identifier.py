
from ultralytics import YOLO
from pathlib import Path

# Get the current working directory
current_dir = Path.cwd()

# Print the current directory
print(f"Current working directory: {current_dir}")

# Load the YOLOv8 model (e.g., yolov11n for a smaller model, or yolov11s for small, yolov11m for medium)
# Note that this will download the model from the internet and store it in the local directory
model = YOLO("yolo11n.pt")

# Train the model
# N.B. Dataset YAML file is in the exported folder from RoboFlow. Rename the folder and put it in the local dir
# E.g. Bowl detection.v4i.yolov11 -> bowlv4
model.train(
    data=current_dir / 'pothole' / 'data.yaml',  # Path to your dataset YAML file
    epochs=20,                    # Number of epochs (adjust as needed)
    imgsz=640,                    # Image size (default 640x640)
    batch=16,                     # Batch size
    device="cpu"                  # Specify device, e.g., '0', '1' etc. for GPU or "cpu" for CPU
)
