import math

import cv2
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')


def preprocess(imgOriginal):
    img_gray = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2GRAY)  # Chuyển ảnh màu sang ảnh xám
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)  # Làm mờ ảnh
    img_thresh = cv2.adaptiveThreshold(img_blur, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19,
                                       9)  # Áp dụng phép nhị phân hóa
    return img_thresh


def Hough_transform(threshold_image, nol=6):
    h, w = threshold_image.shape[:2]
    linesP = cv2.HoughLinesP(threshold_image, 1, np.pi / 180, 50, None, 50, 10)
    dist = []
    for i in range(0, len(linesP)):
        l = linesP[i][0]
        d = math.sqrt((l[0] - l[2]) ** 2 + (l[1] - l[3]) ** 2)
        if d < 0.5 * max(h, w):
            d = 0
        dist.append(d)

    dist = np.array(dist).reshape(-1, 1, 1)
    linesP = np.concatenate([linesP, dist], axis=2)
    linesP = sorted(linesP, key=lambda x: x[0][-1], reverse=True)[:nol]

    return linesP


def rotation_angle(linesP):
    angles = []
    for i in range(0, len(linesP)):
        l = linesP[i][0].astype(int)  # Lấy tọa độ của các đường thẳng
        p1 = (l[0], l[1])  # Tọa độ điểm đầu của đường thẳng
        p2 = (l[2], l[3])  # Tọa độ điểm cuối của đường thẳng
        doi = (l[1] - l[3])  # Cạnh đối của tam giác vuông
        ke = abs(l[0] - l[2])  # Cạnh kề của tam giác vuông
        if ke == 0:
            angle = 90
        else:
            angle = math.atan(doi / ke) * (180.0 / math.pi)  # Tính góc giữa đường thẳng và trục hoành
        if abs(angle) > 45:  # Nếu góc lớn hơn 45 độ tức là đường thẳng gần với trục tung
            angle = (90 - abs(angle)) * angle / abs(angle)
        angles.append(angle)  # Thêm góc vào mảng angles

    angles = list(filter(lambda x: (abs(x > 3) and abs(x < 15)), angles))  # Lọc các góc từ 3 đến 15 độ
    if not angles:  # If the angles is empty
        angles = list([0])
    angle = np.array(angles).mean()  # Tính góc trung bình
    return angle


def rotate_LP(img, angle):
    height, width = img.shape[:2]
    ptPlateCenter = width / 2, height / 2
    rotationMatrix = cv2.getRotationMatrix2D(ptPlateCenter, -angle, 1.0)
    rotated_img = cv2.warpAffine(img, rotationMatrix, (width, height))
    return rotated_img


def draw_lines(image, lines):
    # Vẽ các đường thẳng lên ảnh
    for line in lines:
        l = line[0].astype(int)
        cv2.line(image, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 2)  # Vẽ đường thẳng màu xanh lá cây
    return image


def preprocess_image(image):
    # Tiền xử lý ảnh
    img_thresh = preprocess(image)
    # Áp dụng biến đổi Hough
    linesP = Hough_transform(img_thresh)
    # Tính góc quay
    angle = rotation_angle(linesP)
    # Quay ảnh
    rotated_img = rotate_LP(image, angle)
    return rotated_img
