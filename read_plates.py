import cv2
import torch
from ultralytics import YOLO
def get_number_from_plates(results_letter):
    letter = []
    for result in results_letter:
        boxes= result.boxes
        for i in range(len(boxes)):
            box = boxes[i]
            box_coordinates = box.xyxy[0].cpu().numpy()  # Get box as [x_min, y_min, x_max, y_max] to cpu in numpy
            prob = box.conf.item()  # Confidence score for the current object
            if prob < 0.5:
                continue
            cls = int(box.cls.item())  # Class index
            class_name = result.names[cls]  # Get the class name from index
            letter.append([box_coordinates, prob, class_name])
    return letter
def sort_letter(letter):
    max_ymax= max([i[0][3] for i in letter])
    line_tren=[]
    line_duoi=[]
    for i in range(len(letter)):
        y_min= letter[i][0][1]
        if y_min < max_ymax/2:
            line_tren.append(letter[i])
        else:
            line_duoi.append(letter[i])
    line_tren= sorted(line_tren, key=lambda x: (x[0][0],x[0][1]))
    line_duoi= sorted(line_duoi, key=lambda x: (x[0][0],x[0][1]))
    return line_tren+line_duoi
def read_number(result):
    letter= get_number_from_plates(result)
    letter_bienso= sort_letter(letter)
    bienso=""
    for i in range(len(letter_bienso)):
        bienso+= letter_bienso[i][2]
    if len(bienso) > 8:
        bienso= bienso[:4]+ "-"+ bienso[4:]
    else:
        bienso= bienso[:3]+ "-"+ bienso[3:]
    return bienso
def main_read(model_letter,image_path):
    if isinstance(image_path, str):
        image_path = cv2.imread(image_path)
    results_letter = model_letter(image_path,verbose=False)
    bienso= read_number(results_letter)
    return bienso