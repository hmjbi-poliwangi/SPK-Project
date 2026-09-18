# src/views/home_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("homeCard")
        card.setStyleSheet("""
            #homeCard {
                background-color: #20222f;
                border: 1px solid #2f3550;
                border-radius: 18px;
                padding: 24px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        icon = QLabel("🎯")
        icon.setStyleSheet("font-size: 40px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Sistem Pendukung Keputusan\nProfile Matching")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #f2c94c;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Pilih menu di samping untuk memulai")
        subtitle.setStyleSheet("font-size: 13.5px; color: #9aa1b0;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(icon)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        layout.addWidget(card)