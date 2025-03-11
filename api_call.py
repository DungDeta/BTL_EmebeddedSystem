import requests
import json
from datetime import datetime
import pytz  # Cài đặt bằng: pip install pytz

def get_current_timestamp():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(tz)
    return current_time.strftime('%B %d, %Y at %I:%M:%S %p UTC%z')

BASE_URL = "https://parking-manager-11a88-default-rtdb.firebaseio.com/parking_history.json"


def post_parking_history(vehicle_plate, user_rf_id, status):
    url = BASE_URL
    data = {
        "vehicle_plate": vehicle_plate,
        "user_rf_id": user_rf_id,
        "status": status,
        "time": get_current_timestamp()
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # In ra status code và nội dung phản hồi để kiểm tra
    print(response.status_code)
    print(response.text)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Không thể parse response từ Firebase. Kiểm tra URL hoặc định dạng dữ liệu."}


def get_parking_history(vehicle_plate, user_rf_id):
    url = BASE_URL
    response = requests.get(url)

    print(response.status_code)
    print(response.text)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Không thể parse response từ Firebase."}


# Gọi thử hàm post_parking_history
print(post_parking_history("11111", "11111", "IN"))
