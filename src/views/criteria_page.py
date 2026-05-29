# src/views/criteria_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QTextEdit
)
from src.models.data_structure import get_connection

class CriteriaPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Form input
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama kriteria")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Deskripsi (opsional)")
        btn_add = QPushButton("Tambah")
        btn_add.clicked.connect(self.add_criteria)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(btn_add)
        layout.addLayout(form_layout)

        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Deskripsi"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Tombol hapus
        btn_delete = QPushButton("Hapus Terpilih")
        btn_delete.clicked.connect(self.delete_criteria)
        layout.addWidget(btn_delete)

    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM criteria ORDER BY id")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(row['name']))
            self.table.setItem(i, 2, QTableWidgetItem(row['description'] if row['description'] else ""))

    def add_criteria(self):
        name = self.name_input.text().strip()
        desc = self.desc_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Nama kriteria tidak boleh kosong.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO criteria (name, description) VALUES (?, ?)", (name, desc))
            conn.commit()
            self.name_input.clear()
            self.desc_input.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menambah: {e}")
        finally:
            conn.close()

    def delete_criteria(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih kriteria yang akan dihapus.")
            return
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        crit_id = int(id_item.text())
        name = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Konfirmasi",
            f"Hapus kriteria '{name}'? Data profil dan penilaian terkait akan ikut terhapus.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM criteria WHERE id = ?", (crit_id,))
                conn.commit()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus: {e}")
            finally:
                conn.close()