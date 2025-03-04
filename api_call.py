import requests

BASE_URL = "http://127.0.0.1:8000/api"

def get_vehicle_info(vehicle_plate):
    url = f"{BASE_URL}/vehicle/{vehicle_plate}/"
    response = requests.get(url)
    return response.json()

def get_user_info(user_rf_id):
    url = f"{BASE_URL}/user/{user_rf_id}/"
    response = requests.get(url)
    return response.json()

def post_parking_history(vehicle_plate, user_rf_id, image_path,time_in, time_out):
    url = f"{BASE_URL}/history/"
    data = {
        "time_in": time_in,
        "time_out": time_out,
        "vehicle_plate": vehicle_plate,
        "user_rf_id": user_rf_id,
        "parking_charge": 3000
    }
    files = {
        "image": open(image_path, "rb")
    }
    response = requests.post(url, data=data, files=files)
    return response.json()

