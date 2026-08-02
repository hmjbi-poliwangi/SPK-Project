"""
Utility untuk Import/Export data JSON.
Bisa digunakan oleh Desktop app (SQLite) maupun Web app (Supabase).
"""

import json
from datetime import datetime


def export_to_json(criteria, departments, department_profiles, alternatives, alternative_scores, rankings, aspects=None):
    """
    Export seluruh data ke format JSON.
    Parameter adalah list of dict dari masing-masing tabel.
    """
    data = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0",
            "app": "SPK Profile Matching"
        },
        "aspects": aspects or [],
        "criteria": criteria,
        "departments": departments,
        "department_profiles": department_profiles,
        "alternatives": alternatives,
        "alternative_scores": alternative_scores,
        "rankings": rankings
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def import_from_json(json_str: str) -> dict:
    """
    Import data dari string JSON.
    Mengembalikan dict dengan keys: criteria, departments, department_profiles,
    alternatives, alternative_scores, rankings.
    """
    data = json.loads(json_str)

    # Validasi struktur minimal
    required_keys = ["criteria", "departments", "department_profiles",
                     "alternatives", "alternative_scores", "rankings"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Format JSON tidak valid: key '{key}' tidak ditemukan.")

    return data


def validate_import_data(data: dict) -> list:
    """
    Validasi data import. Mengembalikan list pesan error (kosong jika valid).
    """
    errors = []

    # Validasi aspects (opsional - untuk kompatibilitas file lama)
    for i, a in enumerate(data.get("aspects", [])):
        if "name" not in a or not a["name"]:
            errors.append(f"Aspek ke-{i+1}: nama tidak boleh kosong")

    # Validasi criteria
    for i, c in enumerate(data["criteria"]):
        if "name" not in c or not c["name"]:
            errors.append(f"Criteria ke-{i+1}: nama tidak boleh kosong")

    # Validasi departments
    for i, d in enumerate(data["departments"]):
        if "name" not in d or not d["name"]:
            errors.append(f"Department ke-{i+1}: nama tidak boleh kosong")

    # Validasi alternatives
    for i, a in enumerate(data["alternatives"]):
        if "name" not in a or not a["name"]:
            errors.append(f"Alternative ke-{i+1}: nama tidak boleh kosong")

    # Validasi department_profiles
    for i, p in enumerate(data["department_profiles"]):
        if "department_id" not in p or "criteria_id" not in p:
            errors.append(f"Department profile ke-{i+1}: department_id dan criteria_id wajib")
        if "target_value" not in p or "weight" not in p:
            errors.append(f"Department profile ke-{i+1}: target_value dan weight wajib")
        if "type" not in p or p.get("type") not in ("core", "secondary"):
            errors.append(f"Department profile ke-{i+1}: type harus 'core' atau 'secondary'")

    # Validasi alternative_scores
    for i, s in enumerate(data["alternative_scores"]):
        if "alternative_id" not in s or "criteria_id" not in s:
            errors.append(f"Alternative score ke-{i+1}: alternative_id dan criteria_id wajib")
        if "value" not in s:
            errors.append(f"Alternative score ke-{i+1}: value wajib")

    return errors