import asyncio
import time

import cv2
import lgpio as GPIO
import torch
from ultralytics import YOLO

import api_call
import mfrc522_test
import predict_plates
import read_plates

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

RFID_in = mfrc522_test.SimpleMFRC522()
RFID_out = mfrc522_test.SimpleMFRC522()


def setup_GPIO():
    h = GPIO.gpiochip_open(0)
    GPIO.gpio_claim_input(h, OPEN_BUTTON)
    GPIO.gpio_claim_input(h, CLOSE_BUTTON)
    GPIO.gpio_claim_input(h, SENSOR_IN)
    GPIO.gpio_claim_input(h, SENSOR_OUT)
    GPIO.gpio_claim_output(h, MOTOR)
    return h


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
    return bienxo


async def handle_exit(h):
    print("Xe ra đang xử lý...")
    rfid = await read_rfid(RFID_out)
    plate = await process_vehicle("SENSOR_OUT", camera_out, model_plates, model_letter)
    print("Đã đọc biển số:", plate)
    if plate:
        history = api_call.get_parking_history(plate, rfid)
        if any(record['time_out'] is None for record in history):
            api_call.post_parking_history(plate, rfid, "OUT")
            print(f"CẬP NHẬT LOG: Biển {plate}")
            GPIO.gpio_write(h, MOTOR, 1)
            await asyncio.sleep(3)
            GPIO.gpio_write(h, MOTOR, 0)
        else:
            print("KHÔNG TÌM THẤY LỊCH SỬ - XE LẠ")


async def handle_entry(h):
    print("Xe vào đang xử lý...")
    rfid = await read_rfid(RFID_in)
    plate = await process_vehicle("SENSOR_IN", camera_in, model_plates, model_letter)
    print("Đã đọc biển số:", plate)
    if plate:
        api_call.post_parking_history(plate, rfid, "IN")
        print(f"ĐÃ LƯU LOG: Biển {plate} - RFID: {rfid}")
        GPIO.gpio_write(h, MOTOR, 1)  # Mở barrier
        await asyncio.sleep(3)  # Giữ barrier mở
        GPIO.gpio_write(h, MOTOR, 0)  # Đóng barrier


async def loop(h):
    while True:
        if GPIO.gpio_read(h, OPEN_BUTTON):
            print("Opening gate")
            GPIO.gpio_write(h, MOTOR, 1)
        if GPIO.gpio_read(h, CLOSE_BUTTON):
            print("Closing gate")
            GPIO.gpio_write(h, MOTOR, 0)
        if GPIO.gpio_read(h, SENSOR_IN) or test:
            await handle_entry(h)
        if GPIO.gpio_read(h, SENSOR_OUT):
            await handle_exit(h)
        await asyncio.sleep(0.1)


h = setup_GPIO()
asyncio.run(loop(h))
