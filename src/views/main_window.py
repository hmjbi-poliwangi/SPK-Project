# src/views/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PySide6.QtCore import Qt
from src.views.home_page import HomePage
from src.views.criteria_page import CriteriaPage
from src.views.department_page import DepartmentPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPK Profile Matching")
        self.resize(900, 600)
        self.setMinimumSize(800, 500)

        # Widget utama
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar / Navbar ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            #sidebar {
                background-color: #ecec13;
            }
            QPushButton {
                color: black;
                background: transparent;
                border: none;
                padding: 15px 10px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1f1f1f;
                color: #f0f0f0
            }
            QPushButton:pressed {
                background-color: #3d3d3d;
            }
            QPushButton#exit_btn {
                margin-top: 20px;
            }
            QPushButton#exit_btn:hover {
                background-color: #e74c3c;
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(0)

        # Judul sidebar
        brand = QLabel("Menu Utama")
        brand.setStyleSheet("color: #f0f0f0; font-size: 18px; font-weight: bold; padding: 10px; background-color: #1d1d1d;")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(brand)
        sidebar_layout.addSpacing(20)

        # Tombol navigasi
        self.btn_home = QPushButton("🏠  Beranda")
        self.btn_kriteria = QPushButton("📋  Kriteria")
        self.btn_departemen = QPushButton("🏢  Departemen")
        self.btn_alternatif = QPushButton("👥  Alternatif")
        self.btn_exit = QPushButton("🚪  Keluar")
        self.btn_exit.setObjectName("exit_btn")

        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_kriteria)
        sidebar_layout.addWidget(self.btn_departemen)
        sidebar_layout.addWidget(self.btn_alternatif)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_exit)

        # --- Area konten (Stacked Widget) ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #1d1d1d;")

        # Halaman-halaman
        self.home_page = HomePage()
        self.kriteria_page = CriteriaPage()
        self.departemen_page = DepartmentPage()
        self.alternatif_page = self._create_placeholder_page("Alternatif")

        self.stacked_widget.addWidget(self.home_page)        # index 0
        self.stacked_widget.addWidget(self.kriteria_page)    # index 1
        self.stacked_widget.addWidget(self.departemen_page)  # index 2
        self.stacked_widget.addWidget(self.alternatif_page)  # index 3

        # Tambahkan sidebar dan konten ke layout utama
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

        # Hubungkan tombol
        self.btn_home.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_kriteria.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_departemen.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.btn_alternatif.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.btn_exit.clicked.connect(self.close)

    def _create_placeholder_page(self, title):
        """Buat halaman sementara dengan label besar."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(title)
        label.setStyleSheet("font-size: 32px; color: #bdc3c7;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return page