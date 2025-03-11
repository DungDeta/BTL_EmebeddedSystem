import cv2

from preprocess import preprocess_image


def predict_plate(model, img):
    print("Predicting...")
    results = model(img, verbose=False)
    print("Done")
    return results


def cut_plates(results_plate, img_path):
    plates = []
    if isinstance(img_path, str):
        img = cv2.imread(img_path)  # Đọc ảnh từ đường dẫn
    else:
        img = img_path
    for result in results_plate:
        boxes = result.boxes  # Bounding boxes cho đối tượng
        probs = result.probs  # Xác suất của phân loại
        plates = []
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Tọa độ của box (x1, y1, x2, y2)
            crop_img = img[y1:y2, x1:x2]
            plates.append(crop_img)
    return plates


def process_plate(plates):
    for i in range(len(plates)):
        plates[i] = preprocess_image(plates[i])
    return plates


def main_image(model, image_path):
    if isinstance(image_path, str):
        image_path = cv2.imread(image_path)
    results_plate = predict_plate(model, image_path)
    plates = cut_plates(results_plate, image_path)
    plates = process_plate(plates)
    return plates
