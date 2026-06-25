import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout_utama = QVBoxLayout()

        self.setWindowTitle("Sistem Pendukukng Keputusan")
        self.resize(1200, 700)

        label_intro = QLabel("Sistem Pendukung Keputusan")
        label_intro.setStyleSheet("font-size: 30px; qproperty-alignment: AlignCenter;")

        layout_utama.addWidget(label_intro)
        kontainer_utama = QWidget()
        kontainer_utama.setLayout(layout_utama)
        self.setCentralWidget(kontainer_utama)