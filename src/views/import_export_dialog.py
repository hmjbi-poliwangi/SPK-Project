"""
Dialog Import / Export Data untuk Desktop App (PySide6).
Menggunakan data_structure.py (SQLite) untuk operasi database.
"""

import json
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QGroupBox, QRadioButton, QButtonGroup,
    QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt

from src.models.data_structure import (
    get_all_aspects, create_aspect,
    get_all_criteria, get_all_departments, get_department_profiles,
    get_all_alternatives, get_alternative_scores, get_db, get_db_read,
    create_criteria, create_department, add_department_profile,
    create_alternative, set_alternative_score,
    clear_all_rankings, clear_department_rankings
)
from src.engine.profile_matching import rank_alternatives
from src.utils.io_utils import export_to_json, import_from_json, validate_import_data
from src.utils.pdf_export import export_rankings_to_pdf, export_all_data_to_pdf


class ImportExportDialog(QDialog):
    def __init__(self, parent, mode="export"):
        """
        mode: "export" atau "import"
        """
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("Export Data" if mode == "export" else "Import Data")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

        layout = QVBoxLayout(self)

        # Judul
        title_text = "📤 Export Data" if mode == "export" else "📥 Import Data"
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ecec13; margin-bottom: 10px;")
        layout.addWidget(title)

        if mode == "export":
            self._build_export_ui(layout)
        else:
            self._build_import_ui(layout)

    # ================================================================
    # EXPORT UI
    # ================================================================
    def _build_export_ui(self, layout):
        # Pilihan format
        format_group = QGroupBox("Pilih Format Export")
        format_group.setStyleSheet("""
            QGroupBox {
                color: #ecec13; font-weight: bold; border: 1px solid #555;
                margin-top: 10px; padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; padding: 0 8px;
            }
        """)
        format_layout = QVBoxLayout(format_group)

        self.format_group = QButtonGroup()
        self.radio_json = QRadioButton("JSON (.json) - Seluruh data")
        self.radio_json.setStyleSheet("color: white; padding: 5px;")
        self.radio_json.setChecked(True)
        self.radio_pdf = QRadioButton("PDF (.pdf) - Laporan lengkap")
        self.radio_pdf.setStyleSheet("color: white; padding: 5px;")
        self.radio_pdf_ranking = QRadioButton("PDF (.pdf) - Ranking per departemen")
        self.radio_pdf_ranking.setStyleSheet("color: white; padding: 5px;")

        self.format_group.addButton(self.radio_json, 1)
        self.format_group.addButton(self.radio_pdf, 2)
        self.format_group.addButton(self.radio_pdf_ranking, 3)

        format_layout.addWidget(self.radio_json)
        format_layout.addWidget(self.radio_pdf)
        format_layout.addWidget(self.radio_pdf_ranking)
        layout.addWidget(format_group)

        # Preview / info
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setStyleSheet("background-color: #1d1d1d; color: #aaa; border: 1px solid #555;")
        self.preview_area.setMaximumHeight(120)
        self.preview_area.setText("Klik 'Export' untuk mengexport data...")
        layout.addWidget(self.preview_area)

        # Tombol
        btn_layout = QHBoxLayout()
        btn_export = QPushButton("💾 Export")
        btn_export.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px 20px; font-weight: bold; border-radius: 4px;")
        btn_export.clicked.connect(self.do_export)
        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px 20px; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _collect_all_data_sqlite(self):
        """Kumpulkan semua data dari SQLite untuk export."""
        aspects = [dict(a) for a in get_all_aspects()]
        criteria = [dict(c) for c in get_all_criteria()]
        departments = [dict(d) for d in get_all_departments()]

        department_profiles = []
        for d in departments:
            profiles = get_department_profiles(d["id"], active_only=False)
            department_profiles.extend([dict(p) for p in profiles])

        alternatives = [dict(a) for a in get_all_alternatives()]
        alternative_scores = []
        for a in alternatives:
            scores = get_alternative_scores(a["id"])
            for criteria_id, value in scores.items():
                alternative_scores.append({
                    "alternative_id": a["id"],
                    "criteria_id": criteria_id,
                    "value": value
                })

        rankings = []
        for d in departments:
            try:
                dept_rankings = rank_alternatives(d["id"])
                rankings.append({
                    "department_id": d["id"],
                    "department_name": d["name"],
                    "rankings": dept_rankings
                })
            except Exception:
                pass

        return {
            "aspects": aspects,
            "criteria": criteria,
            "departments": departments,
            "department_profiles": department_profiles,
            "alternatives": alternatives,
            "alternative_scores": alternative_scores,
            "rankings": rankings
        }

    def _get_rankings_per_dept_sqlite(self):
        """Ambil ranking per departemen untuk PDF."""
        departments = get_all_departments()
        result = {}
        for d in departments:
            try:
                rankings = rank_alternatives(d["id"])
                result[d["name"]] = rankings
            except Exception:
                result[d["name"]] = []
        return result

    def do_export(self):
        selected = self.format_group.checkedId()
        try:
            data = self._collect_all_data_sqlite()

            if selected == 1:  # JSON
                json_str = export_to_json(
                    criteria=data["criteria"],
                    departments=data["departments"],
                    department_profiles=data["department_profiles"],
                    alternatives=data["alternatives"],
                    alternative_scores=data["alternative_scores"],
                    rankings=data["rankings"],
                    aspects=data["aspects"]
                )
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Simpan JSON", "spk_export.json",
                    "JSON Files (*.json)"
                )
                if not file_path:
                    return
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                QMessageBox.information(self, "Sukses", f"Data berhasil di-export ke:\n{file_path}")

            elif selected == 2:  # PDF Laporan Lengkap
                rankings_per_dept = self._get_rankings_per_dept_sqlite()
                pdf_buf = export_all_data_to_pdf(
                    criteria=data["criteria"],
                    departments=data["departments"],
                    alternatives=data["alternatives"],
                    rankings_per_department=rankings_per_dept
                )
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Simpan PDF", "spk_laporan.pdf",
                    "PDF Files (*.pdf)"
                )
                if not file_path:
                    return
                with open(file_path, "wb") as f:
                    f.write(pdf_buf.read())
                QMessageBox.information(self, "Sukses", f"Laporan PDF berhasil disimpan:\n{file_path}")

            elif selected == 3:  # PDF Ranking per Departemen
                departments = get_all_departments()
                for d in departments:
                    rankings = rank_alternatives(d["id"])
                    criteria = get_all_criteria()
                    pdf_buf = export_rankings_to_pdf(
                        department_name=d["name"],
                        rankings=rankings,
                        criteria_list=[c["name"] for c in criteria]
                    )
                    safe_name = d["name"].replace(" ", "_")
                    default_name = f"ranking_{safe_name}.pdf"
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, f"Simpan PDF - {d['name']}", default_name,
                        "PDF Files (*.pdf)"
                    )
                    if file_path:
                        with open(file_path, "wb") as f:
                            f.write(pdf_buf.read())
                QMessageBox.information(self, "Sukses", "Semua PDF ranking berhasil disimpan.")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export gagal:\n{str(e)}")

    # ================================================================
    # IMPORT UI
    # ================================================================
    def _build_import_ui(self, layout):
        info = QLabel(
            "Pilih file JSON untuk di-import.\n"
            "Data yang akan di-import: Kriteria, Departemen, Profil, Alternatif, Nilai.\n"
            "Data dengan nama yang sudah ada akan dilewati (skip)."
        )
        info.setStyleSheet("color: #ccc; padding: 10px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Preview area
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setStyleSheet("background-color: #1d1d1d; color: #aaa; border: 1px solid #555;")
        self.preview_area.setPlaceholderText("Pilih file JSON untuk melihat pratinjau...")
        layout.addWidget(self.preview_area)

        # Tombol
        btn_layout = QHBoxLayout()
        btn_select = QPushButton("📂 Pilih File JSON")
        btn_select.setStyleSheet("background-color: #3498db; color: white; padding: 10px 20px; font-weight: bold; border-radius: 4px;")
        btn_select.clicked.connect(self.select_import_file)
        btn_import = QPushButton("📥 Import")
        btn_import.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px 20px; font-weight: bold; border-radius: 4px;")
        btn_import.clicked.connect(self.do_import)
        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px 20px; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_select)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_import)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.selected_file = None

    def select_import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File JSON", "", "JSON Files (*.json)"
        )
        if not file_path:
            return
        self.selected_file = file_path
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read(2000)  # Preview 2000 chars
            self.preview_area.setText(f"File: {os.path.basename(file_path)}\n\n{content[:500]}...")
        except Exception as e:
            self.preview_area.setText(f"Error membaca file: {str(e)}")

    def do_import(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Peringatan", "Pilih file JSON terlebih dahulu.")
            return

        try:
            with open(self.selected_file, "r", encoding="utf-8") as f:
                json_str = f.read()

            data = import_from_json(json_str)

            # Validasi
            errors = validate_import_data(data)
            if errors:
                detail = "\n".join(errors[:10])
                QMessageBox.critical(self, "Validasi Gagal", f"Data tidak valid:\n{detail}")
                return

            # Konfirmasi
            counts = f"Aspek: {len(data.get('aspects', []))}\n"
            counts += f"Kriteria: {len(data['criteria'])}\n"
            counts += f"Departemen: {len(data['departments'])}\n"
            counts += f"Profil: {len(data['department_profiles'])}\n"
            counts += f"Alternatif: {len(data['alternatives'])}"
            confirm = QMessageBox.question(
                self, "Konfirmasi Import",
                f"Data yang akan di-import:\n{counts}\n\nLanjutkan?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

            # 0. Import aspects
            aspect_map = {}
            for a in data.get("aspects", []):
                try:
                    new_id = create_aspect(a["name"], a.get("weight", 1.0))
                    aspect_map[a.get("id")] = new_id
                except Exception:
                    pass

            # 1. Import criteria
            criteria_map = {}
            for c in data["criteria"]:
                try:
                    new_id = create_criteria(c["name"], c.get("description"))
                    criteria_map[c.get("id")] = new_id
                except Exception:
                    pass

            # 2. Import departments
            dept_map = {}
            for d in data["departments"]:
                try:
                    new_id = create_department(d["name"])
                    dept_map[d.get("id")] = new_id
                except Exception:
                    pass

            # 3. Import department_profiles (dengan aspect_id)
            for p in data["department_profiles"]:
                try:
                    dept_id = dept_map.get(p["department_id"])
                    crit_id = criteria_map.get(p["criteria_id"])
                    aspect_id = aspect_map.get(p.get("aspect_id")) if p.get("aspect_id") else None
                    if dept_id and crit_id:
                        add_department_profile(
                            dept_id, crit_id,
                            p["target_value"], p["weight"], p["type"],
                            aspect_id=aspect_id
                        )
                except Exception:
                    pass

            # 4. Import alternatives
            alt_map = {}
            for a in data["alternatives"]:
                try:
                    new_id = create_alternative(
                        a["name"], a.get("nim", ""),
                        a.get("prodi", ""), a.get("kelas", ""),
                        a.get("additional_info")
                    )
                    alt_map[a.get("id")] = new_id
                except Exception:
                    pass

            # 5. Import alternative_scores
            for s in data["alternative_scores"]:
                try:
                    alt_id = alt_map.get(s["alternative_id"])
                    crit_id = criteria_map.get(s["criteria_id"])
                    if alt_id and crit_id:
                        set_alternative_score(alt_id, crit_id, s["value"])
                except Exception:
                    pass

            clear_all_rankings()
            QMessageBox.information(self, "Sukses", f"Import berhasil!\n"
                f"Aspek: {len(aspect_map)}\n"
                f"Kriteria: {len(criteria_map)}\n"
                f"Departemen: {len(dept_map)}\n"
                f"Alternatif: {len(alt_map)}")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import gagal:\n{str(e)}")