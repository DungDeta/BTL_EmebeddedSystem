import time

import cv2
import torch
from ultralytics import YOLO

import predict_plates
import read_plates

device = 'cuda' if torch.cuda.is_available() else "cpu"
model_plates = YOLO("../model/plates_detection.pt").to(device)
model_letter = YOLO('../model/letter_detection.pt').to(device)

# Sample image path
sample_image_path = "../test_data/input_img.jpg"


def test_models():
    start_time = time.time()

    # Read the sample image
    frame = cv2.imread(sample_image_path)
    if frame is None:
        print("Failed to read image")
        return

    # Predict plates
    plates = predict_plates.main_image(model_plates, frame)
    if not plates:
        print("No plates detected")
        return

    # Read plate numbers
    bienxo = read_plates.main_read(model_letter, plates[0])
    print("Detected plate number:", bienxo)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")


if __name__ == "__main__":
    test_models()
