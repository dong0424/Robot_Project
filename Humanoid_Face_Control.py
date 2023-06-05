import sys
import time
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QDialog, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
import cv2 
import numpy as np
from keras.models import load_model  
from PyQt5.QtGui import QPixmap, QImage


# Serial 객체를 생성
ser = None

# 로봇의 액션을 정의
ACTIONS = {
    'greeting': 18,
}

# Load the model
model = load_model("keras_Model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

# CAMERA can be 0 or 1 based on default camera of your computer
camera = cv2.VideoCapture(0)

# Load the haarcascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def execute_action(action):
    if action not in ACTIONS:
        print(f'액션 {action}은 존재하지 않습니다.')
        return

    ActionRobot(ACTIONS[action])

def ActionDelay(d):
    delay_times = {
        1: 1, 2: 1, 3: 1, 4: 1, 5: 1,
        6: 1, 7: 1, 8: 1, 9: 1,
        10: 1, 11: 1, 12: 1, 13: 1,
        22: 1, 23: 1, 28: 1, 29: 1,
        240: 5, 
        17: 15, 18: 15,
        16: 7, 19: 7, 84: 7, 94: 7,
        115: 7, 116: 7, 241: 7
    }

    if d in delay_times:
            time.sleep(delay_times[d])
    else:
        time.sleep(1)
        
def ActionRobot(exeIndex):
    prohibited_indices = [
        14, 15, 20, 21, 37,
        38, 53, 54, 73, 74,
        95, 96, 97, 113, 114,
        117, 118
    ]
    
    if exeIndex in prohibited_indices:
        return

    exeCmd = [
        0xff, 0xff, 0x4c, 0x53, 0x00,
        0x00, 0x00, 0x00, 0x30, 0x0c,
        0x03, exeIndex, 0x00, 100, 0x54
    ]

    exeCmd[14] = sum(exeCmd[6:14])

    ser.write(bytes(exeCmd))
    time.sleep(0.1)
    ActionDelay(exeIndex)

class PortSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("포트 선택")
        self.resize(300, 200)

        layout = QVBoxLayout(self)

        label = QLabel("사용 가능한 Serial Port를 선택하세요:", self)
        layout.addWidget(label)

        self.port_combo = QComboBox(self)
        layout.addWidget(self.port_combo)

        refresh_button = QPushButton("새로 고침", self)
        refresh_button.clicked.connect(self.refresh_ports)
        layout.addWidget(refresh_button)

        ok_button = QPushButton("확인", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        cancel_button = QPushButton("취소", self)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.refresh_ports()

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def get_selected_port(self):
        return self.port_combo.currentText()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("휴머노이드 얼굴인식 프로그램")
        self.setFixedSize(800, 600)  # 창의 크기를 800x600으로 고정합니다.

        self.label_title = QLabel("휴머노이드 얼굴인식 프로그램", self)
        self.label_title.setGeometry(10, 20, 781, 31)
        self.label_title.setAlignment(Qt.AlignCenter)
        font = self.label_title.font()
        font.setPointSize(22)
        self.label_title.setFont(font)

        self.button_port = QPushButton("포트 연결", self)
        self.button_port.setGeometry(480, 160, 291, 51)
        self.button_port.setFont(font)
        self.button_port.clicked.connect(self.handle_port_connect)

        self.webcam_button = QPushButton("웹캠 시작", self)
        self.webcam_button.setGeometry(70, 160, 181, 51)
        self.webcam_button.setFont(font)
        self.webcam_button.clicked.connect(self.start_webcam)

        self.face_detection_timer = QTimer()
        self.face_detection_timer.timeout.connect(self.handle_face_detection)
        
        self.webcam_view = QLabel(self)
        self.webcam_view.setGeometry(250, 250, 480, 360)  # 웹캠 화면 위치와 크기를 설정합니다.

    def handle_port_connect(self):
        dialog = PortSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_port = dialog.get_selected_port()

        global ser, BT  # ser와 BT를 전역으로 사용
        try:
            ser = serial.Serial(selected_port, 115200)
            if ser.isOpen():
                print(f'{selected_port}와 성공적으로 연결되었습니다.')
                # 연결에 성공하면 시리얼 객체를 BT로 설정
                BT = ser
            else:
                print(f'{selected_port}와의 연결에 실패하였습니다.')
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
	
        self.face_detection_timer.start(1000)

    def start_webcam(self):
        self.webcam_timer = QTimer(self)
        self.webcam_timer.timeout.connect(self.update_webcam_view)
        self.webcam_timer.start(30)

        # 웹캠 시작 시 얼굴 인식 타이머도 시작
        self.face_detection_timer.start(1000)

    def update_webcam_view(self):
        ret, image = camera.read()
        if ret:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR 포맷을 사용하므로, RGB 포맷으로 바꿉니다.
            h, w, c = image.shape
            qimg = QImage(image.data, w, h, w*c, QImage.Format_RGB888)  # QImage 객체를 생성합니다.
            pixmap = QPixmap.fromImage(qimg)  # QPixmap 객체를 생성합니다.
            self.webcam_view.setPixmap(pixmap) 

    def handle_face_detection(self):
        ret, image = camera.read()
        if ret:
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                face_image = gray[y:y + h, x:x + w] 
                face_image = cv2.resize(face_image, (224, 224))  
                face_image = face_image / 255.0  
                face_image = np.expand_dims(face_image, axis=0)

               
                predictions = model.predict(face_image)[0]  
                confidence = max(predictions)  

                if confidence > 0.7:  
                    execute_action('greeting')

        # 웹캠의 영상을 라벨에 표시합니다.
        h, w, c = image.shape
        qimg = QImage(image.data, w, h, w*c, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.webcam_view.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
