import cv2
import sys
import time
import mysql.connector
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QImage, QPixmap
import serial
import os

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",  
        database="park_system"
    )
    cursor = db.cursor()
    print("MySQL bağlantısı başarılı!")
except mysql.connector.Error as err:
    print(f"MySQL bağlantı hatası: {err}")
    db = None

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)  

class ParkingSystem(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dinamik Park Sistemi")
        self.setGeometry(100, 100, 800, 600)

        self.line_positions = [100, 250, 400]  #yatay
        self.line_colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255)]  # Yeşil, Mavi, Kırmızı
        self.led_signals = [b'G', b'B', b'R']

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.cap = cv2.VideoCapture(0)
        self.is_recording = False
        self.record_start_time = None
        self.video_writer = None
        self.video_filename = ""

    def init_ui(self):
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()

        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)

        self.date_time_label = QLabel()
        self.layout.addWidget(self.date_time_label)

        self.sliders = []
        for i in range(3):
            slider = QSlider(Qt.Horizontal)
            slider.setRange(50, 750)
            slider.setValue(self.line_positions[i])
            slider.valueChanged.connect(self.update_line_positions)
            self.sliders.append(slider)
            self.layout.addWidget(slider)

        self.save_button = QPushButton("Çizgi Konumlarını Kaydet")
        self.save_button.clicked.connect(self.save_line_positions)
        self.layout.addWidget(self.save_button)

        self.record_button = QPushButton("Kayıt Başlat")
        self.record_button.clicked.connect(self.toggle_recording)
        self.layout.addWidget(self.record_button)

        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def update_line_positions(self):
        self.line_positions = [slider.value() for slider in self.sliders]

    def save_line_positions(self):
        if db:
            try:
                cursor.execute("DELETE FROM line_positions")
                cursor.execute(
                    "INSERT INTO line_positions (position_1, position_2, position_3) VALUES (%s, %s, %s)", 
                    (self.line_positions[0], self.line_positions[1], self.line_positions[2])
                )
                db.commit()
                print("Çizgi konumları kaydedildi!")
            except mysql.connector.Error as err:
                print(f"Veritabanı hatası: {err}")

    def toggle_recording(self):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd_HH-mm-ss")
        
        if self.is_recording:
            self.is_recording = False
            self.record_button.setText("Kayıt Başlat")
            
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

            status = "Durduruldu"

            if db:
                try:
                    cursor.execute("INSERT INTO park_records (timestamp, status, video_path) VALUES (%s, %s, %s)", 
                                   (current_time, status, self.video_filename))
                    db.commit()
                    print(f"Kayıt tamamlandı: {self.video_filename}")
                except mysql.connector.Error as err:
                    print(f"Veritabanı hatası: {err}")

        else:
            self.is_recording = True
            self.record_start_time = time.time()
            self.record_button.setText("Kayıt Durdur")
            status = "Başlatıldı"

            self.video_filename = f"videos/park_record_{current_time}.avi"
            os.makedirs("videos", exist_ok=True)

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 20
            frame_size = (int(self.cap.get(3)), int(self.cap.get(4)))
            self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, fps, frame_size)

            print(f"Kayıt başladı: {self.video_filename}")

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        sorted_lines = sorted(zip(self.line_positions, self.line_colors, self.led_signals))

        for pos, color, _ in sorted_lines:
            cv2.line(frame, (0, pos), (frame.shape[1], pos), color, 2)

        car_top_y = self.detect_car_top(frame)
        led_signal = b'O'  # Varsayılan LED kapalı

        for pos, _, signal in sorted_lines:
            if car_top_y < pos:
                led_signal = signal
                break

        arduino.write(led_signal)
        self.date_time_label.setText(QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate))

        if self.is_recording and self.video_writer:
            self.video_writer.write(frame)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(image))

    def detect_car_top(self, frame):
        height, width, _ = frame.shape
        for y in range(height):
            pixel_value = frame[y, width // 2]
            if pixel_value[0] < 100 and pixel_value[1] < 100 and pixel_value[2] < 100:
                return y
        return height

    def closeEvent(self, event):
        self.cap.release()
        arduino.close()
        if self.video_writer:
            self.video_writer.release()
        if db:
            db.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingSystem()
    window.show()
    sys.exit(app.exec_())
