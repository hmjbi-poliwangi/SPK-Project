# src/views/alternative_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QLabel
)
from PySide6.QtCore import Qt
from src.models.data_structure import (
    get_all_alternatives, create_alternative, update_alternative,
    delete_alternative, get_all_departments, get_alternative_scores,
    set_alternative_score, get_department_profiles, get_db_read,
    get_department_alternatives
)


class AlternativePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1d1d1d; color: #f0f0f0;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("👥 Manajemen Alternatif (Kandidat)")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ecec13;")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.btn_tambah = QPushButton("+ Tambah Alternatif")
        self.btn_tambah.setStyleSheet("""
            QPushButton {
                background-color: #ecec13; color: #1d1d1d;
                padding: 8px 16px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #f5f530; }
        """)
        self.btn_tambah.clicked.connect(self.open_add_dialog)
        toolbar.addWidget(self.btn_tambah)

        toolbar.addStretch()
        toolbar.addWidget(QLabel("Filter Departemen:"))
        self.filter_dept = QComboBox()
        self.filter_dept.setStyleSheet("background-color: #2b2b2b; color: white; padding: 4px; border: 1px solid #555;")
        self.filter_dept.addItem("Semua", None)
        self.filter_dept.currentIndexChanged.connect(self.load_data)
        toolbar.addWidget(self.filter_dept)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Departemen", "Info Tambahan", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
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

        self.load_departments()
        self.load_data()

    def load_departments(self):
        depts = get_all_departments()
        self.filter_dept.clear()
        self.filter_dept.addItem("Semua", None)
        for d in depts:
            self.filter_dept.addItem(d['name'], d['id'])

    def load_data(self):
        dept_id = self.filter_dept.currentData()
        if dept_id:
            alts = get_department_alternatives(dept_id)
        else:
            alts = get_all_alternatives()

        self.table.setRowCount(len(alts))
        for row, alt in enumerate(alts):
            self.table.setItem(row, 0, QTableWidgetItem(str(alt["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(alt["name"]))
            with get_db_read() as conn:
                dept_row = conn.execute("SELECT name FROM departments WHERE id = ?", (alt["department_id"],)).fetchone()
                dept_name = dept_row["name"] if dept_row else "???"
            self.table.setItem(row, 2, QTableWidgetItem(dept_name))
            self.table.setItem(row, 3, QTableWidgetItem(alt["additional_info"] or ""))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            btn_detail = QPushButton("Nilai")
            btn_detail.setStyleSheet("background-color: #9b59b6; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_detail.clicked.connect(lambda checked, aid=alt["id"]: self.open_scores_dialog(aid))

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_edit.clicked.connect(lambda checked, aid=alt["id"]: self.open_edit_dialog(aid))

            btn_delete = QPushButton("Hapus")
            btn_delete.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_delete.clicked.connect(lambda checked, aid=alt["id"]: self.delete_alternative(aid))

            actions_layout.addWidget(btn_detail)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            self.table.setCellWidget(row, 4, actions_widget)

    def open_add_dialog(self):
        dialog = AlternativeFormDialog(self, mode="add")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def open_edit_dialog(self, alt_id):
        dialog = AlternativeFormDialog(self, mode="edit", alternative_id=alt_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def open_scores_dialog(self, alt_id):
        dialog = ScoreDialog(self, alt_id)
        dialog.exec()

    def delete_alternative(self, alt_id):
        confirm = QMessageBox.question(
            self, "Konfirmasi", "Hapus alternatif ini beserta semua nilainya?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                delete_alternative(alt_id)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class AlternativeFormDialog(QDialog):
    def __init__(self, parent, mode="add", alternative_id=None):
        super().__init__(parent)
        self.mode = mode
        self.alternative_id = alternative_id
        self.setWindowTitle("Tambah Alternatif" if mode == "add" else "Edit Alternatif")
        self.setMinimumSize(400, 200)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("background-color: #1d1d1d; color: white; padding: 5px; border: 1px solid #555;")

        self.dept_combo = QComboBox()
        self.dept_combo.setStyleSheet("background-color: #1d1d1d; color: white; padding: 4px; border: 1px solid #555;")
        self.load_departments()

        self.info_input = QLineEdit()
        self.info_input.setStyleSheet("background-color: #1d1d1d; color: white; padding: 5px; border: 1px solid #555;")

        form.addRow("Nama:", self.name_input)
        form.addRow("Departemen:", self.dept_combo)
        form.addRow("Info Tambahan:", self.info_input)
        layout.addLayout(form)

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

        if self.mode == "edit":
            self.load_alt_data()

    def load_departments(self):
        depts = get_all_departments()
        for d in depts:
            self.dept_combo.addItem(d['name'], d['id'])

    def load_alt_data(self):
        with get_db_read() as conn:
            row = conn.execute("SELECT * FROM alternatives WHERE id = ?", (self.alternative_id,)).fetchone()
            if row:
                self.name_input.setText(row['name'])
                idx = self.dept_combo.findData(row['department_id'])
                if idx >= 0:
                    self.dept_combo.setCurrentIndex(idx)
                self.info_input.setText(row['additional_info'] or "")

    def save(self):
        name = self.name_input.text().strip()
        dept_id = self.dept_combo.currentData()
        info = self.info_input.text().strip() or None

        if not name or dept_id is None:
            QMessageBox.warning(self, "Validasi", "Nama dan Departemen harus diisi.")
            return

        try:
            if self.mode == "add":
                create_alternative(name, dept_id, info)
            else:
                update_alternative(self.alternative_id, name=name, department_id=dept_id, additional_info=info)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ScoreDialog(QDialog):
    def __init__(self, parent, alternative_id):
        super().__init__(parent)
        self.alternative_id = alternative_id
        self.setWindowTitle("Nilai Kriteria Alternatif")
        self.setMinimumSize(500, 300)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

        layout = QVBoxLayout(self)

        with get_db_read() as conn:
            alt = conn.execute("SELECT * FROM alternatives WHERE id = ?", (alternative_id,)).fetchone()
            dept = conn.execute("SELECT name FROM departments WHERE id = ?", (alt['department_id'],)).fetchone()
        title = QLabel(f"Nilai untuk: {alt['name']} ({dept['name']})")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ecec13;")
        layout.addWidget(title)

        profiles = get_department_profiles(alt['department_id'], active_only=True)
        current_scores = get_alternative_scores(alternative_id)

        self.score_inputs = {}

        for prof in profiles:
            criteria_name = prof['criteria_name']
            criteria_id = prof['criteria_id']
            target = prof['target_value']
            current_val = current_scores.get(criteria_id, 0.0)

            row_layout = QHBoxLayout()
            lbl = QLabel(f"{criteria_name} (target: {target})")
            lbl.setStyleSheet("color: white;")
            spin = QDoubleSpinBox()
            spin.setStyleSheet("background-color: #1d1d1d; color: white; border: 1px solid #555;")
            spin.setRange(0, 9999)
            spin.setDecimals(2)
            spin.setValue(current_val)
            row_layout.addWidget(lbl)
            row_layout.addWidget(spin)
            layout.addLayout(row_layout)
            self.score_inputs[criteria_id] = spin

        btn_save = QPushButton("Simpan Semua Nilai")
        btn_save.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        btn_save.clicked.connect(self.save_all)
        layout.addWidget(btn_save, alignment=Qt.AlignmentFlag.AlignRight)

    def save_all(self):
        try:
            for criteria_id, spin in self.score_inputs.items():
                value = spin.value()
                set_alternative_score(self.alternative_id, criteria_id, value)
            QMessageBox.information(self, "Sukses", "Nilai berhasil disimpan.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))