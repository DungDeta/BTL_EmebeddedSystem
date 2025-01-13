import asyncio
import time
import torch
from ultralytics import YOLO
from GPIOEmulator.EmulatorGUI import GPIO
import picamera as picam
import predict_plates
import read_plates
import mfrc522

device = 'cuda' if torch.cuda.is_available() else "cpu"
model_plates = YOLO("model/plates_detection.pt").to(device)
model_letter = YOLO('model/letter_detection.pt').to(device)

OPEN_BUTTON = 14
CLOSE_BUTTON = 15
SENSOR_IN = 23
SENSOR_OUT = 24
MOTOR = 25
camera_in = picam.PiRGBArray(picam.PiCamera())
camera_out = picam.PiRGBArray(picam.PiCamera())
RFID_in = mfrc522.SimpleMFRC522()
RFID_out = mfrc522.SimpleMFRC522()

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OPEN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(CLOSE_BUTTON, GPIO.IN)
    GPIO.setup(SENSOR_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SENSOR_OUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(MOTOR, GPIO.OUT)

async def read_rfid(RFID, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        rfid = RFID.read("RFID0001")
        if rfid != '':
            print(f"RFID read successfully: {rfid}")
            return rfid
        await asyncio.sleep(1)  # Avoid busy-waiting
    print("RFID read timeout")
    return False

async def process_vehicle(sensor, camera, model_plates, model_letter):
    print(f"Vehicle detected at {sensor}")
    # Giả lập đọc ảnh từ camera (bất đồng bộ)
    await asyncio.sleep(0.1)  # Thay thế bằng thao tác bất đồng bộ thực tế nếu có

    # Giả lập nhận dạng biển số
    img = camera.array(input="test_data/input_img.jpg")
    plates = await asyncio.to_thread(predict_plates.main_image, model_plates, img)  # Chạy YOLO trong thread
    bienxo = await asyncio.to_thread(read_plates.main_read, model_letter, plates[0])  # Chạy đọc biển số trong thread
    return bienxo
async def loop():
    while True:
        if GPIO.input(OPEN_BUTTON):
            print("Opening gate")
            GPIO.output(MOTOR, GPIO.HIGH)

        if GPIO.input(CLOSE_BUTTON):
            print("Closing gate")
            GPIO.output(MOTOR, GPIO.LOW)

        if GPIO.input(SENSOR_IN):
            # Gọi bất đồng bộ từng hàm
            rfid = await read_rfid(RFID_in)
            bienxo = await process_vehicle("SENSOR_IN", camera_in, model_plates, model_letter)
            print(f"RFID: {rfid}, Biển số: {bienxo}")
        if GPIO.input(SENSOR_OUT):
            rfid = await read_rfid(RFID_out)
            bienxo = await process_vehicle("SENSOR_OUT", camera_out, model_plates, model_letter)
            print(f"RFID: {rfid}, Biển số: {bienxo}")
        await asyncio.sleep(0.1)
setup_GPIO()
asyncio.run(loop())