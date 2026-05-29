# src/views/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget
)
from PySide6.QtCore import Qt
from .departments_page import DepartmentsPage
from .criteria_page import CriteriaPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPK Profile Matching")
        self.setMinimumSize(800, 600)

        # Widget utama
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tombol navigasi
        nav_layout = QHBoxLayout()
        self.btn_dept = QPushButton("Departemen")
        self.btn_crit = QPushButton("Kriteria")
        self.btn_profile = QPushButton("Profil Departemen")
        self.btn_ranking = QPushButton("Penilaian & Ranking")
        # Disable halaman yang belum tersedia
        self.btn_profile.setEnabled(False)
        self.btn_ranking.setEnabled(False)

        nav_layout.addWidget(self.btn_dept)
        nav_layout.addWidget(self.btn_crit)
        nav_layout.addWidget(self.btn_profile)
        nav_layout.addWidget(self.btn_ranking)
        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        # Stacked widget untuk halaman
        self.stack = QStackedWidget()
        self.dept_page = DepartmentsPage()
        self.crit_page = CriteriaPage()
        self.stack.addWidget(self.dept_page)   # index 0
        self.stack.addWidget(self.crit_page)   # index 1

        main_layout.addWidget(self.stack)

        # Koneksi tombol
        self.btn_dept.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_crit.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        # Nanti tombol lainnya akan dihubungkan ke halaman yang sesuai

        # Tampilkan halaman pertama
        self.stack.setCurrentIndex(0)