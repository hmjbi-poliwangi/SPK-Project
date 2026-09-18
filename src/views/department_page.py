# src/views/department_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox,
    QLabel, QFrame, QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt
from src.models.data_structure import (
    get_all_departments, create_department, update_department,
    delete_department, get_department_profiles,
    add_department_profile, update_department_profile,
    delete_department_profile, get_all_criteria, get_db_read,
    clear_department_rankings, get_all_aspects
)

from src.engine.profile_matching import rank_alternatives

class DepartmentPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1d1d1d; color: #f0f0f0;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        # Judul
        title = QLabel("🏢 Manajemen Departemen")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ecec13;")
        layout.addWidget(title)

        # Toolbar
        toolbar = QHBoxLayout()
        btn_tambah = QPushButton("+ Tambah Departemen")
        btn_tambah.setStyleSheet("""
            QPushButton {
                background-color: #ecec13; color: #1d1d1d;
                padding: 8px 16px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #f5f530; }
        """)
        btn_tambah.clicked.connect(self.open_add_dialog)
        toolbar.addWidget(btn_tambah)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Tabel departemen
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Departemen", "Jumlah Profil", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
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
        """Tampilkan semua departemen."""
        departments = get_all_departments()
        self.table.setRowCount(len(departments))
        for row, dept in enumerate(departments):
            self.table.setItem(row, 0, QTableWidgetItem(str(dept["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(dept["name"]))

            # Hitung jumlah profil aktif
            profiles = get_department_profiles(dept["id"], active_only=False)
            active_count = sum(1 for p in profiles if p["is_active"])
            self.table.setItem(row, 2, QTableWidgetItem(str(active_count)))

            # Aksi
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_edit.clicked.connect(lambda checked, did=dept["id"]: self.open_edit_dialog(did))

            btn_delete = QPushButton("Hapus")
            btn_delete.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_delete.clicked.connect(lambda checked, did=dept["id"]: self.delete_department(did))

            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            self.table.setCellWidget(row, 3, actions_widget)

    def open_add_dialog(self):
        """Dialog tambah departemen baru."""
        dialog = DepartmentFormDialog(self, mode="add")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def open_edit_dialog(self, department_id):
        dialog = DepartmentDetailDialog(self, department_id)
        dialog.exec()
        self.load_data()

    def delete_department(self, department_id):
        confirm = QMessageBox.question(
            self, "Konfirmasi", "Hapus departemen ini? Semua profil dan alternatif akan terhapus.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                delete_department(department_id)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


# -------------------------------------------------------------------
# Dialog Tambah/Ubah Nama Departemen (sederhana)
# -------------------------------------------------------------------
class DepartmentFormDialog(QDialog):
    def __init__(self, parent, mode="add", department_id=None, current_name=""):
        super().__init__(parent)
        self.mode = mode
        self.department_id = department_id
        self.setWindowTitle("Tambah Departemen" if mode == "add" else "Ubah Nama Departemen")
        self.setMinimumSize(400, 150)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name_input = QLineEdit(current_name)
        self.name_input.setStyleSheet("background-color: #1d1d1d; color: white; padding: 5px; border: 1px solid #555;")
        form.addRow("Nama Departemen:", self.name_input)
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

    def save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validasi", "Nama departemen harus diisi.")
            return
        try:
            if self.mode == "add":
                create_department(name)
            else:
                update_department(self.department_id, name)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# -------------------------------------------------------------------
# Dialog Lengkap: Edit Departemen + Profil
# -------------------------------------------------------------------
class DepartmentDetailDialog(QDialog):
    def __init__(self, parent, department_id):
        super().__init__(parent)
        self.department_id = department_id
        self.setWindowTitle("Detail Departemen")
        self.setMinimumSize(650, 500)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

        layout = QVBoxLayout(self)

        # Nama departemen dan tombol ubah
        header_layout = QHBoxLayout()
        self.dept_name_label = QLabel()
        self.dept_name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ecec13;")
        btn_rename = QPushButton("Ubah Nama")
        btn_rename.setStyleSheet("background-color: #3498db; color: white; padding: 6px 12px; border-radius: 3px;")
        btn_rename.clicked.connect(self.rename_department)
        header_layout.addWidget(self.dept_name_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_rename)
        layout.addLayout(header_layout)

        # Tabel profil
        layout.addWidget(QLabel("Kriteria Profil:"))
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(6)
        self.profile_table.setHorizontalHeaderLabels(["ID", "Kriteria", "Target", "Bobot (inf.)", "Tipe", "Aksi"])
        self.profile_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.profile_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.profile_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.profile_table.setStyleSheet("""
            QTableWidget {
                background-color: #1d1d1d; gridline-color: #444;
            }
            QTableWidget::item { color: #f0f0f0; padding: 5px; }
            QHeaderView::section {
                background-color: #333; color: white; padding: 6px;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.profile_table)

        # Tombol tambah profil
        btn_add_profile = QPushButton("+ Tambah Kriteria")
        btn_add_profile.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        btn_add_profile.clicked.connect(self.add_profile)
        layout.addWidget(btn_add_profile, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_ranking = QPushButton("🏆 Peringkat Alternatif")
        btn_ranking.setStyleSheet("background-color: #9b59b6; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        btn_ranking.clicked.connect(self.show_ranking)
        layout.addWidget(btn_ranking, alignment=Qt.AlignmentFlag.AlignLeft)
        

        # Tombol tutup
        btn_close = QPushButton("Tutup")
        btn_close.setStyleSheet("background-color: #7f8c8d; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

        self.load_department_data()
        self.load_profiles()

    def load_department_data(self):
        with get_db_read() as conn:
            row = conn.execute("SELECT name FROM departments WHERE id = ?", (self.department_id,)).fetchone()
            if row:
                self.dept_name_label.setText(row["name"])

    def rename_department(self):
        dialog = DepartmentFormDialog(
            self, mode="edit", department_id=self.department_id,
            current_name=self.dept_name_label.text()
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_department_data()

    def load_profiles(self):
        profiles = get_department_profiles(self.department_id)
        self.profile_table.setRowCount(len(profiles))
        for row, prof in enumerate(profiles):
            self.profile_table.setItem(row, 0, QTableWidgetItem(str(prof["id"])))
            self.profile_table.setItem(row, 1, QTableWidgetItem(prof["criteria_name"]))
            self.profile_table.setItem(row, 2, QTableWidgetItem(str(prof["target_value"])))
            self.profile_table.setItem(row, 3, QTableWidgetItem(f"{prof['weight']:.2f}"))
            type_display = "Core" if prof["type"] == "core" else "Secondary"
            if not prof["is_active"]:
                type_display += " (nonaktif)"
            self.profile_table.setItem(row, 4, QTableWidgetItem(type_display))

            # Aksi
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            btn_edit_prof = QPushButton("Edit")
            btn_edit_prof.setStyleSheet("background-color: #f39c12; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_edit_prof.clicked.connect(lambda checked, pid=prof["id"]: self.edit_profile(pid))

            btn_del_prof = QPushButton("Hapus")
            btn_del_prof.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 3px; padding: 4px 8px;")
            btn_del_prof.clicked.connect(lambda checked, pid=prof["id"]: self.delete_profile(pid))

            actions_layout.addWidget(btn_edit_prof)
            actions_layout.addWidget(btn_del_prof)
            self.profile_table.setCellWidget(row, 5, actions_widget)

    def add_profile(self):
        dialog = ProfileFormDialog(self, department_id=self.department_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            clear_department_rankings(self.department_id)   # tambahkan
            self.load_profiles()

    def edit_profile(self, profile_id):
        dialog = ProfileFormDialog(self, department_id=self.department_id, profile_id=profile_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            clear_department_rankings(self.department_id)
            self.load_profiles()

    def delete_profile(self, profile_id):
        confirm = QMessageBox.question(...)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                delete_department_profile(profile_id)
                clear_department_rankings(self.department_id)   # tambahkan
                self.load_profiles()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def show_ranking(self):
        rankings = rank_alternatives(self.department_id)
        dialog = RankingDialog(self, rankings)
        dialog.exec()


# -------------------------------------------------------------------
# Dialog Tambah/Edit Profil
# -------------------------------------------------------------------
class ProfileFormDialog(QDialog):
    def __init__(self, parent, department_id, profile_id=None):
        super().__init__(parent)
        self.department_id = department_id
        self.profile_id = profile_id
        self.setWindowTitle("Tambah Profil" if profile_id is None else "Edit Profil")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Pilih kriteria
        self.criteria_combo = QComboBox()
        self.criteria_combo.setStyleSheet("background-color: #1d1d1d; color: white; padding: 4px; border: 1px solid #555;")
        self.load_criteria()
        form.addRow("Kriteria:", self.criteria_combo)

        # Target value
        self.target_input = QDoubleSpinBox()
        self.target_input.setStyleSheet("background-color: #1d1d1d; color: white; border: 1px solid #555;")
        self.target_input.setRange(0, 9999)
        self.target_input.setDecimals(2)
        form.addRow("Target Value:", self.target_input)

        # Weight
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setStyleSheet("background-color: #1d1d1d; color: white; border: 1px solid #555;")
        self.weight_input.setRange(0, 1)
        self.weight_input.setDecimals(3)
        self.weight_input.setSingleStep(0.05)
        form.addRow("Bobot (informatif):", self.weight_input)

        # Aspek
        self.aspect_combo = QComboBox()
        self.aspect_combo.setStyleSheet("background-color: #1d1d1d; color: white; padding: 4px; border: 1px solid #555;")
        self.load_aspects()
        form.addRow("Aspek:", self.aspect_combo)

        # Tipe core/secondary
        self.type_group = QButtonGroup()
        self.radio_core = QRadioButton("Core")
        self.radio_secondary = QRadioButton("Secondary")
        self.radio_core.setStyleSheet("color: white;")
        self.radio_secondary.setStyleSheet("color: white;")
        self.type_group.addButton(self.radio_core, 0)
        self.type_group.addButton(self.radio_secondary, 1)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_core)
        radio_layout.addWidget(self.radio_secondary)
        form.addRow("Tipe Faktor:", radio_layout)

        # Aktif (hanya untuk edit)
        self.active_check = QCheckBox("Profil Aktif")
        self.active_check.setChecked(True)
        self.active_check.setStyleSheet("color: white;")
        if profile_id is None:
            self.active_check.hide()  # untuk tambah, default aktif
        form.addRow(self.active_check)

        layout.addLayout(form)

        # Simpan / Batal
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

        if profile_id:
            self.load_profile_data()

    def load_criteria(self):
        criteria_list = get_all_criteria()
        for crit in criteria_list:
            self.criteria_combo.addItem(crit["name"], crit["id"])

    def load_aspects(self):
        self.aspect_combo.addItem("(Tidak Ada)", None)
        aspects = get_all_aspects()
        for asp in aspects:
            self.aspect_combo.addItem(f"{asp['name']} (bobot: {asp['weight']})", asp["id"])

    def load_profile_data(self):
        with get_db_read() as conn:
            row = conn.execute("SELECT * FROM department_profiles WHERE id = ?", (self.profile_id,)).fetchone()
            if row:
                index = self.criteria_combo.findData(row["criteria_id"])
                if index >= 0:
                    self.criteria_combo.setCurrentIndex(index)
                self.target_input.setValue(row["target_value"])
                self.weight_input.setValue(row["weight"])
                if row["type"] == "core":
                    self.radio_core.setChecked(True)
                else:
                    self.radio_secondary.setChecked(True)
                self.active_check.setChecked(bool(row["is_active"]))
                aid = row["aspect_id"]
                if aid:
                    idx = self.aspect_combo.findData(aid)
                    if idx >= 0:
                        self.aspect_combo.setCurrentIndex(idx)

    def save(self):
        criteria_id = self.criteria_combo.currentData()
        target = self.target_input.value()
        weight = self.weight_input.value()
        type_ = "core" if self.radio_core.isChecked() else "secondary"
        is_active = 1 if self.active_check.isChecked() else 0
        aspect_id = self.aspect_combo.currentData()

        try:
            if self.profile_id is None:
                add_department_profile(self.department_id, criteria_id, target, weight, type_, aspect_id=aspect_id)
            else:
                update_department_profile(
                    self.profile_id,
                    target_value=target,
                    weight=weight,
                    type_=type_,
                    is_active=is_active,
                    aspect_id=aspect_id
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class RankingDialog(QDialog):
    def __init__(self, parent, rankings):
        super().__init__(parent)
        self.setWindowTitle("Peringkat Alternatif (Profile Matching)")
        self.setMinimumSize(500, 350)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")
        layout = QVBoxLayout(self)

        title = QLabel("Hasil Peringkat Alternatif")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ecec13; margin-bottom: 10px;")
        layout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Nama Alternatif", "Total Skor"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1d1d1d; gridline-color: #444;
            }
            QTableWidget::item { color: #f0f0f0; padding: 5px; }
            QHeaderView::section {
                background-color: #333; color: white; padding: 6px;
                border: 1px solid #444;
            }
        """)
        table.setRowCount(len(rankings))
        for row, r in enumerate(rankings):
            table.setItem(row, 0, QTableWidgetItem(r['name']))
            table.setItem(row, 1, QTableWidgetItem(f"{r['total']:.3f}"))
        layout.addWidget(table)

        btn_close = QPushButton("Tutup")
        btn_close.setStyleSheet("background-color: #7f8c8d; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)