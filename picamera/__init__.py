import time

import cv2

"""
Module này giả lập thư viện picamera của Raspberry Pi sử dụng opencv để chạy trên máy tính 
"""


class PiCamera:
    def __init__(self, resolution=(640, 480), framerate=30):
        """
        Khởi tạo camera
        :param resolution: Độ phân giải của camera
        :param framerate: Số frame trên giây
        """
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():  # Kiểm tra camera có mở được không
            raise RuntimeError("Cannot open camera. Make sure a webcam is connected.")
        # Set các chỉ số cho camera
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.camera.set(cv2.CAP_PROP_FPS, framerate)
        time.sleep(2)

        actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
        if (actual_width != resolution[0]) or (
                actual_height != resolution[1]):  # Kiểm tra xem camera có hỗ trợ độ phân giải không
            print(
                f"Warning: Requested resolution {resolution} not fully supported. Actual: ({actual_width}, {actual_height})")
        if actual_fps != framerate:
            print(f"Warning: Requested framerate {framerate} not fully supported. Actual: {actual_fps}")

    def capture(self,input, output, format='bgr', quality=90):
        """
        Chụp ảnh từ camera và lưu vào file
        :param output:  Đường dẫn lưu ảnh
        :param format:  Định dạng ảnh
        :param quality:  Chất lượng ảnh
        :return:
        """
        if input:
            img = cv2.imread(input)
            cv2.imwrite(output, img)
            print(f"Image saved to {output}")
            return
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError('Failed to capture image')
        if format == 'bgr':
            cv2.imwrite(output, frame)
        elif format == 'rgb':
            cv2.imwrite(output, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        elif format == 'gray':
            cv2.imwrite(output, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        elif format == 'jpeg':
            cv2.imwrite(output, frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        elif format == 'png':
            cv2.imwrite(output, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), quality])
        else:
            raise ValueError(f'Invalid format: {format}')
        print(f"Image saved to {output} in format {format}")

    def close(self):
        """
        Đóng camera
        :return:
        """
        self.camera.release()
        print("Camera released.")


class PiRGBArray:
    def __init__(self, camera, size=None):
        self.camera = camera
        self.size = size

    def array(self, input=None):
        """
        Chụp ảnh từ camera và trả về dưới dạng mảng numpy
        :return:
        """
        if input:
            return cv2.imread(input)
        ret, frame = self.camera.camera.read()
        if not ret:
            raise RuntimeError('Failed to capture image')
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if self.size:
            frame_rgb = cv2.resize(frame_rgb, self.size)
        return frame_rgb
