import time
import cv2
import torch
from ultralytics import YOLO
import matplotlib.pyplot as plt
import predict_plates
import read_plates

device = 'cuda' if torch.cuda.is_available() else "cpu"
model_plates = YOLO("../model/plates_detection.pt").to(device)
model_letter = YOLO('../model/letter_detection.pt').to(device)

# Sample image path
sample_image_path = "../test_data/input_img.jpg"

def show_image(title, image):
    plt.figure()
    plt.title(title)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

def test_models():
    start_time = time.time()

    # Read the sample image
    frame = cv2.imread(sample_image_path)
    if frame is None:
        print("Failed to read image")
        return

    # Display the original image
    show_image("Original Image", frame)

    # Predict plates
    plates = predict_plates.main_image(model_plates, frame)
    if not plates:
        print("No plates detected")
        return

    # Display the detected plates
    show_image("Plate",plates[0])

    # Read plate numbers
    bienxo = read_plates.main_read(model_letter, plates[0])
    print("Detected plate number:", bienxo)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

if __name__ == "__main__":
    test_models()