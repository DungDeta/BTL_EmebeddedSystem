import json
from datetime import datetime

import pytz
import requests


def get_current_timestamp():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz)
    return current_time.strftime('%B %d, %Y at %I:%M:%S %p UTC%z')


BASE_URL = "https://parking-manager-11a88-default-rtdb.firebaseio.com/parking_history"


def post_parking_history(vehicle_plate, user_rf_id, status):
    url = f"{BASE_URL}.json"
    data = {
        "vehicle_plate": vehicle_plate,
        "user_rf_id": user_rf_id,
        "status": status,
        "time_in": get_current_timestamp(),
        "time_out": None
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response.status_code)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Không thể parse response từ Firebase. Kiểm tra URL hoặc định dạng dữ liệu."}


def get_parking_history(vehicle_plate, user_rf_id):
    url = f"{BASE_URL}.json"
    response = requests.get(url)

    print(response.status_code)
    try:
        data = response.json()
        for record_id, record in data.items():
            if record.get('vehicle_plate') == vehicle_plate and record.get('user_rf_id') == user_rf_id and record.get("time_out") is None:
                return record_id,record
        return {"error": "Không tìm thấy bản ghi phù hợp."}
    except requests.exceptions.JSONDecodeError:
        return {"error": "Không thể parse response từ Firebase."}

def put_parking_history(record_id, vehicle_plate, user_rf_id,time_in):
    url = f"{BASE_URL}/{record_id}.json"
    data = {
        "vehicle_plate": vehicle_plate,
        "user_rf_id": user_rf_id,
        "status": "OUT",
        "time_in": time_in,
        "time_out": get_current_timestamp(),
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, headers=headers, data=json.dumps(data))
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Cannot parse response from Firebase. Check URL or data format."}