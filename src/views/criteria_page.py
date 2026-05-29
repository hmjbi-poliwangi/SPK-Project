# src/views/criteria_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QDialog, QTextEdit, QDialogButtonBox
)
from src.models.data_structure import get_connection

class CriteriaPage(QWidget):
    def __init__(self):
        super().__init__()
        self.editing_id = None
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

        self.btn_save = QPushButton("Tambah")
        self.btn_save.clicked.connect(self.save_criteria)

        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.clicked.connect(self.reset_form)
        self.btn_cancel.setEnabled(False)

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.btn_save)
        form_layout.addWidget(self.btn_cancel)
        layout.addLayout(form_layout)

        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Deskripsi"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Double klik untuk lihat deskripsi lengkap
        self.table.cellDoubleClicked.connect(self.show_description_popup)
        layout.addWidget(self.table)

        # Tombol aksi
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
        cursor.execute("SELECT id, name, description FROM criteria ORDER BY id")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(row['name']))
            self.table.setItem(i, 2, QTableWidgetItem(row['description'] if row['description'] else ""))

    def save_criteria(self):
        name = self.name_input.text().strip()
        desc = self.desc_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Nama kriteria tidak boleh kosong.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            if self.editing_id is None:
                cursor.execute("INSERT INTO criteria (name, description) VALUES (?, ?)", (name, desc))
            else:
                cursor.execute("UPDATE criteria SET name = ?, description = ? WHERE id = ?", (name, desc, self.editing_id))
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
            QMessageBox.information(self, "Info", "Pilih kriteria yang akan diedit.")
            return
        id_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        desc_item = self.table.item(row, 2)
        if not id_item or not name_item:
            return
        self.editing_id = int(id_item.text())
        self.name_input.setText(name_item.text())
        self.desc_input.setText(desc_item.text() if desc_item else "")
        self.btn_save.setText("Simpan")
        self.btn_cancel.setEnabled(True)

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Pilih kriteria yang akan dihapus.")
            return
        id_item = self.table.item(row, 0)
        name = self.table.item(row, 1).text()
        if not id_item:
            return
        crit_id = int(id_item.text())

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
                if self.editing_id == crit_id:
                    self.reset_form()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus: {e}")
            finally:
                conn.close()

    def reset_form(self):
        self.editing_id = None
        self.name_input.clear()
        self.desc_input.clear()
        self.btn_save.setText("Tambah")
        self.btn_cancel.setEnabled(False)
    

    def show_description_popup(self, row, col):
        """Menampilkan pop-up deskripsi lengkap kriteria yang dipilih."""
        # Ambil nama dan deskripsi dari baris yang diklik
        name_item = self.table.item(row, 1)
        desc_item = self.table.item(row, 2)
        if not name_item:
            return
        name = name_item.text()
        desc = desc_item.text() if desc_item else "(tidak ada deskripsi)"

        # Buat dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Deskripsi Kriteria: {name}")
        dialog.resize(400, 250)

        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setPlainText(desc)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec()