import sys
from PySide6.QtWidgets import QApplication
from src.views.main_window import MainWindow
from src.models.data_structure import create_tables

if __name__ == "__main__":
    create_tables()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())