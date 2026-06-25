# src/views/home_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Sistem Pendukung Keputusan\nProfile Matching")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffff1a;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Pilih menu di samping untuk memulai")
        subtitle.setStyleSheet("font-size: 14px; color: #fff;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)