from MFRC522Pi5 import MFRC522
import lgpio as GPIO
def uidToString(uid):
    mystring = ""
    for i in uid:
        mystring = format(i, '02X') + mystring
    return mystring
reader=MFRC522.MFRC522()
while True:
        (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status == reader.MI_OK:
                print("Card detected")
                (status, uid) = reader.MFRC522_SelectTagSN()
                if status == reader.MI_OK:
                        print("Card read UID: %s" % uidToString(uid))
                else:
                        print("Authentication error")