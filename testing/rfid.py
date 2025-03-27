from MFRC522Pi5 import MFRC522
import lgpio as GPIO
CS_PIN_1 = 8
CS_PIN_2 = 7
def uidToString(uid):
    mystring = ""
    for i in uid:
        mystring = format(i, '02X') + mystring
    return mystring


reader = MFRC522.MFRC522()
h=GPIO.gpiochip_open(0)
GPIO.gpio_claim_output(h, CS_PIN_1)
GPIO.gpio_claim_input(h, CS_PIN_2)
GPIO.gpio_write(h, CS_PIN_1, 1)
GPIO.gpio_write(h, CS_PIN_2, 1)
# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")
while True:
    # Scan for cards
    GPIO.gpio_write(h, CS_PIN_1, 0)
    GPIO.gpio_write(h, CS_PIN_2, 1)
    (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
    if status == reader.MI_OK:
        print("Card detected")
        (status, uid) = reader.MFRC522_SelectTagSN()
        if status == reader.MI_OK:
            print("Card read UID: %s" % uidToString(uid))
        else:
            print("Authentication error")
