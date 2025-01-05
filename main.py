from GPIOEmulator.EmulatorGUI import GPIO
import picamera as picam # Thư viện giả lập camera
import predict_plates
import read_plates
import mfrc522 # Thư viện giả lập RFID
import time

# Set up the GPIO
OPEN_BUTTON = 14
CLOSE_BUTTON = 15
SENSOR_IN = 23
SENSOR_OUT = 24
MOTOR = 25
camera_in = picam.PiRGBArray(picam.PiCamera())
camera_out = picam.PiRGBArray(picam.PiCamera())
RFID_in=mfrc522.SimpleMFRC522()
RFID_out=mfrc522.SimpleMFRC522()
def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OPEN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(CLOSE_BUTTON, GPIO.IN)
    GPIO.setup(SENSOR_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SENSOR_OUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(MOTOR, GPIO.OUT)

def loop():
    """
    Hàm lặp vô hạn để kiểm tra các cảm biến cùng với việc handle các nút nhấn mở cửa
    Nếu có xe vào thì chụp ảnh và dự đoán biển số sau đó kiểm tra RFID
    :return:
    """
    while True:
        if GPIO.input(OPEN_BUTTON):
            print("Nhấn nút mở cổng")
            GPIO.output(MOTOR, GPIO.HIGH)
        if GPIO.input(CLOSE_BUTTON):
            print("Nhấn nút đóng cổng")
            GPIO.output(MOTOR, GPIO.LOW)
        if GPIO.input(SENSOR_IN):
            print("Phát hiện xe vào")
            img= camera_in.array(input="test_data/input_img.jpg")
            plates=predict_plates.main_image(img)
            bienxo=read_plates.main_read(plates[0])
            check_rfid(RFID_in, bienxo)
        if GPIO.input(SENSOR_OUT):
            print("Phát hiện xe ra")
            img= camera_in.array(input="test_data/input_img.jpg")
            plates=predict_plates.main_image(img)
            bienxo=read_plates.main_read(plates[0])
            check_rfid(RFID_out, bienxo)
def check_rfid(RFID,expected_rfid, timeout=10):
    """
    Hàm kiểm tra RFID
    :param RFID: Đối tượng RFID để đọc
    :param expected_rfid: RFID cần so sánh
    :param timeout:  Thời gian chờ
    :return:
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        rfid = RFID.read()
        if rfid == expected_rfid:
            print("Đọc thẻ thành công")
            return True
        print("Đọc thẻ thất bại")
        time.sleep(1)  # Tránh lặp quá nhanh
    print("Hết thời gian chờ RFID")
    return False
setup_GPIO()
loop()