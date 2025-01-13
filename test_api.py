import requests

BASE_URL = "http://127.0.0.1:8000/api"

def check_rfid(vehicle_plate, user_rf_id):
    url = f"{BASE_URL}/check-rfid/"
    data = {
        "vehicle_plate": vehicle_plate,
        "user_rf_id": user_rf_id
    }
    response = requests.post(url, data=data)
    print("Check RFID Response:", response.json())

def parking_log(vehicle_plate, user_rf_id, parking_charge, image_path):
    url = f"{BASE_URL}/parking-log/"
    data = {
        "vehicle_plate": vehicle_plate,
        "user_rf_id": user_rf_id,
        "parking_charge": parking_charge
    }
    files = {
        "image": open(image_path, "rb")
    }
    response = requests.post(url, data=data, files=files)
    print("Parking Log Response:", response.json())

if __name__ == "__main__":
    # Test CheckRFIDAPI
    check_rfid("00A-0000", "RFID123456")

    # Test ParkingLogAPI
    parking_log("00A-0000", "RFID123456", 3000, "test_data/input_img.jpg")