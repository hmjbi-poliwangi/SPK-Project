# src/views/departments_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from src.models.data_structure import get_connection

class DepartmentsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Form tambah
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama departemen")
        btn_add = QPushButton("Tambah")
        btn_add.clicked.connect(self.add_department)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(btn_add)
        layout.addLayout(form_layout)

        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Departemen"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Tombol hapus
        btn_delete = QPushButton("Hapus Terpilih")
        btn_delete.clicked.connect(self.delete_department)
        layout.addWidget(btn_delete)

    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM departments ORDER BY id")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(row['name']))

    def add_department(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Nama tidak boleh kosong.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
            conn.commit()
            self.name_input.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menambah: {e}")
        finally:
            conn.close()

    def delete_department(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih departemen yang akan dihapus.")
            return
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        dept_id = int(id_item.text())
        name = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Konfirmasi",
            f"Hapus departemen '{name}'? Semua data terkait akan ikut terhapus.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
                conn.commit()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus: {e}")
            finally:
                conn.close()