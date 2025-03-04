import asyncio
import time
import torch
from ultralytics import YOLO
import RPi.GPIO as GPIO
import cv2
import predict_plates
import read_plates
import mfrc522
import api_call

device = 'cuda' if torch.cuda.is_available() else "cpu"
model_plates = YOLO("model/plates_detection.pt").to(device)
model_letter = YOLO('model/letter_detection.pt').to(device)

OPEN_BUTTON = 14
CLOSE_BUTTON = 15
SENSOR_IN = 23
SENSOR_OUT = 24
MOTOR = 25

test_data = "test_data/input_img.jpg"
camera_in = cv2.VideoCapture(0)
camera_out = cv2.VideoCapture(1)
test = True

RFID_in = mfrc522.SimpleMFRC522()
RFID_out = mfrc522.SimpleMFRC522()

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OPEN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(CLOSE_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SENSOR_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SENSOR_OUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(MOTOR, GPIO.OUT)
    GPIO.setwarnings(False)

async def read_rfid(RFID, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        rfid = RFID.read("RFID0001")
        if rfid != '':
            print(f"RFID read successfully: {rfid}")
            return rfid
        await asyncio.sleep(1)
    print("RFID read timeout")
    return False

async def process_vehicle(sensor, camera, model_plates, model_letter):
    print(f"Vehicle detected at {sensor}")
    await asyncio.sleep(0.1)

    frame = cv2.imread(test_data)
    plates = await asyncio.to_thread(predict_plates.main_image, model_plates, frame)
    if not plates:
        print("No plates detected")
        return None

    bienxo = await asyncio.to_thread(read_plates.main_read, model_letter, plates[0])
    return bienxo, frame

async def check_ownership_and_log(vehicle_plate, user_rf_id, frame,time_in, time_out):
    user= api_call.get_user_info(user_rf_id)
    vehicle= api_call.get_vehicle_info(vehicle_plate)
    if vehicle["owner_id"] != user["id"]:
        print("Unauthorized vehicle")
        return
    else:
        print("Authorized vehicle")
        img_path= f"test_data/{vehicle_plate}.jpg"
        cv2.imwrite(img_path, frame)
        api_call.post_parking_history(vehicle_plate, user_rf_id, img_path,time_in, time_out)

async def loop():
    while True:
        if GPIO.input(OPEN_BUTTON):
            print("Opening gate")
            GPIO.output(MOTOR, GPIO.HIGH)

        if GPIO.input(CLOSE_BUTTON):
            print("Closing gate")
            GPIO.output(MOTOR, GPIO.LOW)

        if GPIO.input(SENSOR_IN) or test:
            rfid = await read_rfid(RFID_in)
            result = await process_vehicle("SENSOR_IN", camera_in, model_plates, model_letter)
            if result is not None:
                bienxo, frame = result
                print(f"RFID: {rfid}, Biển số: {bienxo}")
                await check_ownership_and_log(bienxo, rfid, frame, time.time(), None)
            else:
                print("Failed to process vehicle")

        if GPIO.input(SENSOR_OUT):
            rfid = await read_rfid(RFID_out)
            result = await process_vehicle("SENSOR_OUT", camera_out, model_plates, model_letter)
            if result is not None:
                bienxo, frame = result
                print(f"RFID: {rfid}, Biển số: {bienxo}")
                await check_ownership_and_log(bienxo, rfid, frame, None, time.time())
            else:
                print("Failed to process vehicle")

        await asyncio.sleep(0.1)

setup_GPIO()
asyncio.run(loop())