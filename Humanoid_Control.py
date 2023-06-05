import sys
import time
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QDialog, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# Serial 객체를 생성
ser = None

# 로봇의 액션을 정의
ACTIONS = {
    'greeting': 18,
    'win': 17,
    'hi': 19,
    'loss': 16,
    'fight': 22
}

def execute_action(action):
    if action not in ACTIONS:
        print(f'액션 {action}은 존재하지 않습니다.')
        return

    ActionRobot(ACTIONS[action])



# ActionDelay 함수와 ActionRobot 함수를 업데이트
def ActionDelay(d):
    delay_times = {
        1: 1, 2: 1, 3: 1, 4: 1, 5: 1,
        6: 1, 7: 1, 8: 1, 9: 1,
        10: 1, 11: 1, 12: 1, 13: 1,
        22: 1, 23: 1, 28: 1, 29: 1,
        # And so on...
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

        self.setWindowTitle("휴머노이드 제어 프로그램")
        self.setFixedSize(800, 600)  # 창의 크기를 800x600으로 고정합니다.

        self.label = QLabel(self)
        self.label.setGeometry(480, 280, 291, 261)
        pixmap = QPixmap("C:/Users/user/Desktop/로봇 수업/picture/Humanoid_Picture.jpg")
        self.label.setPixmap(pixmap)

        self.label_title = QLabel("휴머노이드 제어 프로그램", self)
        self.label_title.setGeometry(10, 20, 781, 31)
        self.label_title.setAlignment(Qt.AlignCenter)
        font = self.label_title.font()
        font.setPointSize(22)
        self.label_title.setFont(font)

        self.button_greeting = QPushButton("인사", self)
        self.button_greeting.setGeometry(70, 160, 181, 51)
        self.button_greeting.setFont(font)
        self.button_greeting.clicked.connect(lambda: execute_action('greeting'))

        self.button_win = QPushButton("Win", self)
        self.button_win.setGeometry(70, 240, 181, 51)
        self.button_win.setFont(font)
        self.button_win.clicked.connect(lambda: execute_action('win'))

        self.button_hi = QPushButton("Hi", self)
        self.button_hi.setGeometry(70, 320, 181, 51)
        self.button_hi.setFont(font)
        self.button_hi.clicked.connect(lambda: execute_action('hi'))

        self.button_loss = QPushButton("Loss", self)
        self.button_loss.setGeometry(70, 400, 181, 51)
        self.button_loss.setFont(font)
        self.button_loss.clicked.connect(lambda: execute_action('loss'))

        self.button_fight = QPushButton("Fight", self)
        self.button_fight.setGeometry(70, 490, 181, 51)
        self.button_fight.setFont(font)
        self.button_fight.clicked.connect(lambda: execute_action('fight'))

        self.button_port = QPushButton("포트 연결", self)
        self.button_port.setGeometry(480, 160, 291, 51)
        self.button_port.setFont(font)
        self.button_port.clicked.connect(self.handle_port_connect)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
