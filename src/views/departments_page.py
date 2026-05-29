# src/views/departments_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from src.models.data_structure import get_connection

class DepartmentsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.editing_id = None  # menyimpan id yang sedang diedit
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Form
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama departemen")

        self.btn_save = QPushButton("Tambah")
        self.btn_save.clicked.connect(self.save_department)

        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.clicked.connect(self.reset_form)
        self.btn_cancel.setEnabled(False)

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.btn_save)
        form_layout.addWidget(self.btn_cancel)
        layout.addLayout(form_layout)

        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Departemen"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)

        # Tombol aksi bawah
        action_layout = QHBoxLayout()
        btn_edit = QPushButton("Edit Terpilih")
        btn_edit.clicked.connect(self.edit_selected)
        btn_delete = QPushButton("Hapus Terpilih")
        btn_delete.clicked.connect(self.delete_selected)

        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        action_layout.addStretch()
        layout.addLayout(action_layout)

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

    def save_department(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Nama tidak boleh kosong.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            if self.editing_id is None:
                # Mode tambah
                cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
            else:
                # Mode edit
                cursor.execute("UPDATE departments SET name = ? WHERE id = ?", (name, self.editing_id))
            conn.commit()
            self.reset_form()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")
        finally:
            conn.close()

    def edit_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih departemen yang akan diedit.")
            return
        id_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        if not id_item or not name_item:
            return
        self.editing_id = int(id_item.text())
        self.name_input.setText(name_item.text())
        self.btn_save.setText("Simpan")
        self.btn_cancel.setEnabled(True)

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih departemen yang akan dihapus.")
            return
        id_item = self.table.item(row, 0)
        name = self.table.item(row, 1).text()
        if not id_item:
            return
        dept_id = int(id_item.text())

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
                if self.editing_id == dept_id:
                    self.reset_form()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus: {e}")
            finally:
                conn.close()

    def reset_form(self):
        self.editing_id = None
        self.name_input.clear()
        self.btn_save.setText("Tambah")
        self.btn_cancel.setEnabled(False)

    def on_selection_changed(self):
        # Tidak melakukan apa-apa, hanya untuk menonaktifkan tombol edit/hapus jika perlu
        pass