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
CS_PIN_1 = 8 # CS_PIN cho RFID Reader thẻ ra
CS_PIN_2 = 7 # CS_PIN cho RFID Reader thẻ vào

test_data = "test_data/input_img.jpg"
camera_in = cv2.VideoCapture(0)
camera_out = cv2.VideoCapture(1)
test = True

RFID_reader= mfrc522_test.SimpleMFRC522()

def setup_GPIO():
    h = GPIO.gpiochip_open(0)
    # Cấu hình các chân GPIO input
    GPIO.gpio_claim_input(h, OPEN_BUTTON)
    GPIO.gpio_claim_input(h, CLOSE_BUTTON)
    GPIO.gpio_claim_input(h, SENSOR_IN)
    GPIO.gpio_claim_input(h, SENSOR_OUT)
    # Cấu hình các chân GPIO output
    GPIO.gpio_claim_output(h, MOTOR)
    GPIO.gpio_claim_output(h, CS_PIN_1)
    GPIO.gpio_claim_output(h, CS_PIN_2)
    # Đặt trạng thái ban đầu cho các chân GPIO để tắt RFID reader
    GPIO.gpio_write(h, CS_PIN_1, 1)
    GPIO.gpio_write(h, CS_PIN_2, 1)
    return h

def select_reader(h, cs_pin):
    GPIO.gpio_write(h, CS_PIN_1, 1)
    GPIO.gpio_write(h, CS_PIN_2, 1)
    GPIO.gpio_write(h, cs_pin, 0)

async def read_rfid(cs_pin, h, timeout=10):
    select_reader(h, cs_pin)
    start_time = time.time()
    while time.time() - start_time < timeout:
        rfid = await asyncio.to_thread(RFID_reader.read,"RFID0001")
        if rfid != '':
            print(f"RFID read successfully: {rfid}")
            GPIO.gpio_write(h, cs_pin, 1)  # Tắt RFID reader
            return rfid
        await asyncio.sleep(1)
    print("RFID read timeout")
    GPIO.gpio_write(h, cs_pin, 1)  # Tắt RFID reader
    return False


async def process_vehicle(camera):
    if test:
        frame = cv2.imread(test_data)
    else:
        ret, frame = camera.read()
        if not ret:
            print("Failed to capture image from camera.")
            return None

    plates = await asyncio.to_thread(predict_plates.main_image, model_plates, frame)
    if not plates:
        print("No plates detected")
        return None

    bienxo = await asyncio.to_thread(read_plates.main_read, model_letter, plates[0])
    return bienxo

async def handle_exit(h):
    print("Xe ra đang xử lý...")
    rfid = await read_rfid(CS_PIN_2, h)
    plate = await process_vehicle(camera_out)
    print("Đã đọc biển số:", plate)
    if plate:
        record_id, record = api_call.get_parking_history(plate, rfid)
        if isinstance(record, dict):
            api_call.put_parking_history(record_id, plate, rfid, record.get("time_in"))
            print(f"CẬP NHẬT LOG: Biển {plate}")
            GPIO.gpio_write(h, MOTOR, 1)
            await asyncio.sleep(5)
            GPIO.gpio_write(h, MOTOR, 0)
        else:
            print("KHÔNG TÌM THẤY LỊCH SỬ - XE LẠ")
    else:
        print("KHÔNG TÌM THẤY LỊCH SỬ - XE LẠ")

async def handle_entry(h):
    print("Xe vào đang xử lý...")
    rfid = await read_rfid(CS_PIN_1, h)
    plate = await process_vehicle(camera_in)
    print("Đã đọc biển số:", plate)
    if plate:
        api_call.post_parking_history(plate, rfid, "IN")
        print(f"ĐÃ LƯU LOG: Biển {plate} - RFID: {rfid}")
        GPIO.gpio_write(h, MOTOR, 1)  # Mở barrier
        await asyncio.sleep(5)  # Giữ barrier mở
        GPIO.gpio_write(h, MOTOR, 0)  # Đóng barrier

async def loop(h):
    while True:
        if GPIO.gpio_read(h, OPEN_BUTTON):
            print("Mở cổng")
            GPIO.gpio_write(h, MOTOR, 1)
        if GPIO.gpio_read(h, CLOSE_BUTTON):
            print("Đóng cổng")
            GPIO.gpio_write(h, MOTOR, 0)
        if GPIO.gpio_read(h, SENSOR_IN):
            await handle_entry(h)
        if GPIO.gpio_read(h, SENSOR_OUT):
            await handle_exit(h)
        await asyncio.sleep(0.1)

h = setup_GPIO()
asyncio.run(loop(h))