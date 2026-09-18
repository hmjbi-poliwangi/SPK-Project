from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QDoubleSpinBox, QLabel
)
from PySide6.QtCore import Qt
from src.models.data_structure import (
    get_all_aspects, create_aspect, update_aspect, delete_aspect
)


class AspectPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #14161f; color: #edeef2;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("📊 Manajemen Aspek")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f2c94c;")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        btn_tambah = QPushButton("+ Tambah Aspek")
        btn_tambah.setStyleSheet("""
            QPushButton {
                background-color: #f2c94c; color: #14161f; border: none;
                padding: 9px 16px; font-weight: bold; border-radius: 8px;
            }
            QPushButton:hover { background-color: #ffd97a; }
            QPushButton:pressed { background-color: #d9a62b; }
        """)
        btn_tambah.clicked.connect(self.open_add_dialog)
        toolbar.addWidget(btn_tambah)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Aspek", "Bobot", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1b1e2a; gridline-color: #3a4054;
                border: 1px solid #3a4054; border-radius: 8px; alternate-background-color: #232838;
            }
            QTableWidget::item { color: #edeef2; padding: 6px; selection-background-color: #3b4361; selection-color: #ffffff; }
            QHeaderView::section { background-color: #262a3a; color: #e6e9f2; padding: 8px; border: 1px solid #3a4054; font-weight: 600; }
            QTableCornerButton::section { background-color: #262a3a; border: 1px solid #3a4054; }
        """)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        aspects = get_all_aspects()
        self.table.setRowCount(len(aspects))
        for row, asp in enumerate(aspects):
            self.table.setItem(row, 0, QTableWidgetItem(str(asp["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(asp["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(asp["weight"])))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background-color: #3d9bf1; color: white; border: none; border-radius: 6px; padding: 6px 11px;")
            btn_edit.clicked.connect(lambda checked, aid=asp["id"], n=asp["name"], w=asp["weight"]: self.open_edit_dialog(aid, n, w))

            btn_delete = QPushButton("Hapus")
            btn_delete.setStyleSheet("background-color: #e5484d; color: white; border: none; border-radius: 6px; padding: 6px 11px;")
            btn_delete.clicked.connect(lambda checked, aid=asp["id"]: self.delete_aspect(aid))

            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            self.table.setCellWidget(row, 3, actions_widget)

    def open_add_dialog(self):
        dialog = AspectFormDialog(self, mode="add")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def open_edit_dialog(self, aspect_id, name, weight):
        dialog = AspectFormDialog(self, mode="edit", aspect_id=aspect_id, current_name=name, current_weight=weight)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def delete_aspect(self, aspect_id):
        confirm = QMessageBox.question(
            self, "Konfirmasi", "Hapus aspek ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                delete_aspect(aspect_id)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class AspectFormDialog(QDialog):
    def __init__(self, parent, mode="add", aspect_id=None, current_name="", current_weight=1.0):
        super().__init__(parent)
        self.mode = mode
        self.aspect_id = aspect_id
        self.setWindowTitle("Tambah Aspek" if mode == "add" else "Edit Aspek")
        self.setMinimumSize(400, 180)
        self.setStyleSheet("background-color: #1f2230; color: #edeef2;")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit(current_name)
        self.name_input.setStyleSheet("background-color: #1b1e2a; color: #ffffff; padding: 7px; border: 1px solid #3a4054; border-radius: 6px;")
        form.addRow("Nama Aspek:", self.name_input)

        self.weight_input = QDoubleSpinBox()
        self.weight_input.setStyleSheet("background-color: #1b1e2a; color: #ffffff; border: 1px solid #3a4054; border-radius: 6px;")
        self.weight_input.setRange(0, 100)
        self.weight_input.setDecimals(2)
        self.weight_input.setValue(current_weight)
        form.addRow("Bobot:", self.weight_input)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("background-color: #2fbf71; color: #ffffff; border: none; padding: 9px 16px; border-radius: 8px; font-weight: bold;")
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("background-color: #55606f; color: #ffffff; border: none; padding: 9px 16px; border-radius: 8px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def save(self):
        name = self.name_input.text().strip()
        weight = self.weight_input.value()
        if not name:
            QMessageBox.warning(self, "Validasi", "Nama aspek harus diisi.")
            return
        try:
            if self.mode == "add":
                create_aspect(name, weight)
            else:
                update_aspect(self.aspect_id, name, weight)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))