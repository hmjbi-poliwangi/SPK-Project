# src/views/criteria_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QListWidget, QLabel, QFrame
)
from PySide6.QtCore import Qt
from src.models.data_structure import (
    get_all_criteria, create_criteria, update_criteria, delete_criteria,
    get_db_read
)

class CriteriaPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1d1d1d; color: #f0f0f0;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        # Judul
        title = QLabel("📋 Manajemen Kriteria")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ecec13;")
        layout.addWidget(title)

        # Toolbar
        btn_tambah = QPushButton("+ Tambah Kriteria")
        btn_tambah.setStyleSheet("""
            QPushButton {
                background-color: #ecec13; color: #1d1d1d;
                padding: 8px 16px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #f5f530; }
        """)
        btn_tambah.clicked.connect(self.open_add_dialog)
        layout.addWidget(btn_tambah, alignment=Qt.AlignmentFlag.AlignLeft)

        # Tabel kriteria
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Deskripsi", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b; gridline-color: #444;
            }
            QTableWidget::item { color: #f0f0f0; padding: 5px; }
            QHeaderView::section {
                background-color: #333; color: white; padding: 6px;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        """Ambil semua kriteria dan tampilkan di tabel."""
        criteria_list = get_all_criteria()
        self.table.setRowCount(len(criteria_list))
        for row, crit in enumerate(criteria_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(crit["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(crit["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(crit["description"] or ""))

            # Tombol aksi
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_edit.clicked.connect(lambda checked, cid=crit["id"]: self.open_edit_dialog(cid))

            btn_delete = QPushButton("Hapus")
            btn_delete.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_delete.clicked.connect(lambda checked, cid=crit["id"]: self.delete_criteria(cid))

            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            self.table.setCellWidget(row, 3, actions_widget)

    def open_add_dialog(self):
        dialog = CriteriaFormDialog(self, mode="add")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def open_edit_dialog(self, criteria_id):
        dialog = CriteriaFormDialog(self, mode="edit", criteria_id=criteria_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def delete_criteria(self, criteria_id):
        confirm = QMessageBox.question(
            self, "Konfirmasi", "Hapus kriteria ini? Semua data terkait juga akan terhapus.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                delete_criteria(criteria_id)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class CriteriaFormDialog(QDialog):
    def __init__(self, parent, mode="add", criteria_id=None):
        super().__init__(parent)
        self.mode = mode
        self.criteria_id = criteria_id
        self.setWindowTitle("Tambah Kriteria" if mode == "add" else "Edit Kriteria")
        self.setMinimumSize(450, 350)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

        layout = QVBoxLayout(self)

        # Form
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("background-color: #1d1d1d; color: white; padding: 5px; border: 1px solid #555;")
        self.desc_input = QTextEdit()
        self.desc_input.setStyleSheet("background-color: #1d1d1d; color: white; border: 1px solid #555;")

        form_layout.addRow("Nama Kriteria:", self.name_input)
        form_layout.addRow("Deskripsi:", self.desc_input)
        layout.addLayout(form_layout)

        # Jika edit, tampilkan daftar departemen pengguna
        if mode == "edit":
            layout.addSpacing(10)
            label_dept = QLabel("Digunakan oleh Departemen:")
            label_dept.setStyleSheet("font-weight: bold; color: #ecec13;")
            layout.addWidget(label_dept)

            self.dept_list = QListWidget()
            self.dept_list.setStyleSheet("background-color: #1d1d1d; color: white; border: 1px solid #555;")
            layout.addWidget(self.dept_list)

            self.load_criteria_data()
            self.load_departments_using_criteria()

        # Tombol simpan & batal
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def load_criteria_data(self):
        """Isi form dengan data kriteria yang akan diedit."""
        with get_db_read() as conn:
            row = conn.execute("SELECT * FROM criteria WHERE id = ?", (self.criteria_id,)).fetchone()
            if row:
                self.name_input.setText(row["name"])
                self.desc_input.setPlainText(row["description"] or "")

    def load_departments_using_criteria(self):
        """Ambil daftar departemen yang menggunakan kriteria ini."""
        with get_db_read() as conn:
            rows = conn.execute("""
                SELECT DISTINCT d.name
                FROM department_profiles dp
                JOIN departments d ON dp.department_id = d.id
                WHERE dp.criteria_id = ?
            """, (self.criteria_id,)).fetchall()
            self.dept_list.clear()
            for row in rows:
                self.dept_list.addItem(row["name"])
            if not rows:
                self.dept_list.addItem("(Tidak ada departemen yang menggunakan kriteria ini)")

    def save(self):
        name = self.name_input.text().strip()
        desc = self.desc_input.toPlainText().strip() or None

        if not name:
            QMessageBox.warning(self, "Validasi", "Nama kriteria harus diisi.")
            return

        try:
            if self.mode == "add":
                create_criteria(name, desc)
            else:
                update_criteria(self.criteria_id, name, desc)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))