import random


class SimpleMFRC522:
    def __init__(self):
        """
        Khởi tạo đối tượng SimpleMFRC522
        """
        pass

    def read(self, random_input=None):
        """
        Đọc dữ liệu từ thẻ RFID. Nếu không có giá trị đầu vào, trả về một ID thẻ mặc định,
        nếu có giá trị random_input, trả về giá trị đó.
        :param random_input: ID thẻ RFID giả lập
        :return: ID thẻ RFID
        """
        if random_input:
            return random_input  # Giả lập thẻ với ID được chỉ định
        return str(random.randint(1000000000, 9999999999))  # Tạo ID thẻ ngẫu nhiên

    def write(self, text):
        """
        Ghi dữ liệu vào thẻ RFID (giả lập).
        :param text: Dữ liệu cần ghi
        """
        print(f"Write: {text}")  # In dữ liệu đã ghi vào thẻ RFID
        return
