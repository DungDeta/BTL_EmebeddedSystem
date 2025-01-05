from GPIOEmulator.EmulatorGUI import GPIO
import picamera as picam
from PIL import Image
import predict_plates
from matplotlib import pyplot as plt
import cv2
# Set up the GPIO
OPEN_BUTTON = 14
CLOSE_BUTTON = 15
SENSOR_IN = 23
SENSOR_OUT = 24
MOTOR = 25
camera_in = picam.PiRGBArray(picam.PiCamera())
camera_out = picam.PiRGBArray(picam.PiCamera())

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OPEN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(CLOSE_BUTTON, GPIO.IN)
    GPIO.setup(SENSOR_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SENSOR_OUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(MOTOR, GPIO.OUT)


def loop():
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
            cv2.imwrite("test_data/plates.jpg", plates[0])
            plt.imshow(plates[0])
            plt.show()
        if GPIO.input(SENSOR_OUT):
            print("Phát hiện xe ra")

setup_GPIO()
loop()