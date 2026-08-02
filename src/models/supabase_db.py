"""
Supabase PostgreSQL database layer untuk Vercel/Web deployment.
Menggantikan SQLite (data_structure.py) untuk environment serverless.

Desktop app (main.py / PySide6) tetap menggunakan SQLite via data_structure.py.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError(
                "SUPABASE_URL dan SUPABASE_KEY harus diisi di environment variables"
            )
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


# -------------------------------------------------------------------
# Inisialisasi tabel (jalankan sekali saat membuat project di Supabase)
# -------------------------------------------------------------------
CREATE_TABLES_SQL = """
-- 1. Nonaktifkan RLS
ALTER TABLE IF EXISTS aspects DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS departments DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS criteria DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS department_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS alternatives DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS alternative_scores DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS department_rankings DISABLE ROW LEVEL SECURITY;

-- 2. Buat tabel aspects (baru)
CREATE TABLE IF NOT EXISTS aspects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0
);

-- Tabel departments
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Tabel criteria
CREATE TABLE IF NOT EXISTS criteria (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Tabel department_profiles (dengan aspect_id)
CREATE TABLE IF NOT EXISTS department_profiles (
    id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    criteria_id INTEGER NOT NULL REFERENCES criteria(id) ON DELETE CASCADE,
    target_value DOUBLE PRECISION NOT NULL,
    weight DOUBLE PRECISION NOT NULL DEFAULT 0,
    type TEXT NOT NULL CHECK(type IN ('core', 'secondary')),
    is_active INTEGER NOT NULL DEFAULT 1,
    aspect_id INTEGER REFERENCES aspects(id) ON DELETE SET NULL,
    UNIQUE(department_id, criteria_id)
);

-- Tabel alternatives
CREATE TABLE IF NOT EXISTS alternatives (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    kelas TEXT NOT NULL,
    prodi TEXT,
    nim TEXT NOT NULL,
    additional_info TEXT
);

-- Tabel alternative_scores
CREATE TABLE IF NOT EXISTS alternative_scores (
    id SERIAL PRIMARY KEY,
    alternative_id INTEGER NOT NULL REFERENCES alternatives(id) ON DELETE CASCADE,
    criteria_id INTEGER NOT NULL REFERENCES criteria(id) ON DELETE CASCADE,
    value DOUBLE PRECISION NOT NULL,
    UNIQUE(alternative_id, criteria_id)
);

-- Tabel department_rankings (cache) - hanya total, tanpa ncf/nsf
CREATE TABLE IF NOT EXISTS department_rankings (
    id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    alternative_id INTEGER NOT NULL REFERENCES alternatives(id) ON DELETE CASCADE,
    total DOUBLE PRECISION NOT NULL,
    UNIQUE(department_id, alternative_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_dept_profiles_dept ON department_profiles(department_id);
CREATE INDEX IF NOT EXISTS idx_dept_profiles_criteria ON department_profiles(criteria_id);
CREATE INDEX IF NOT EXISTS idx_alt_scores_alt ON alternative_scores(alternative_id);
CREATE INDEX IF NOT EXISTS idx_alt_scores_criteria ON alternative_scores(criteria_id);
CREATE INDEX IF NOT EXISTS idx_dept_rankings_dept ON department_rankings(department_id);
"""


def create_tables():
    """
    Informasi pembuatan tabel untuk Supabase.
    
    Fungsi ini tidak bisa otomatis membuat tabel karena Supabase
    tidak mengizinkan eksekusi SQL via REST API tanpa setup khusus.
    
    WAJIB: Buat tabel manual via Supabase Dashboard:
    1. Buka https://supabase.com → dashboard project kamu
    2. Klik "SQL Editor" di sidebar kiri
    3. Klik "New Query"
    4. Copy paste SQL dari CREATE_TABLES_SQL di file ini
    5. Klik "Run" (▶️)
    """
    import warnings
    warnings.warn(
        "Tabel Supabase belum dibuat! Jalankan SQL dari CREATE_TABLES_SQL "
        "via Supabase SQL Editor. Lihat file DEPLOY_GUIDE.md untuk panduan lengkap."
    )


# ===================================================================
# 0. CRUD Aspects
# ===================================================================
def get_all_aspects() -> list:
    supabase = get_supabase()
    resp = supabase.table("aspects").select("*").order("id").execute()
    return resp.data if resp.data else []


def get_aspect_by_id(aspect_id: int) -> dict:
    supabase = get_supabase()
    resp = supabase.table("aspects").select("*").eq("id", aspect_id).execute()
    if not resp.data:
        raise ValueError(f"Aspect dengan id {aspect_id} tidak ditemukan.")
    return resp.data[0]


def create_aspect(name: str, weight: float = 1.0) -> int:
    supabase = get_supabase()
    data = {"name": name, "weight": float(weight)}
    resp = supabase.table("aspects").insert(data).execute()
    if not resp.data:
        raise ValueError(f"Aspek dengan nama '{name}' sudah ada.")
    return resp.data[0]["id"]


def update_aspect(aspect_id: int, name: str = None, weight: float = None) -> bool:
    supabase = get_supabase()
    data = {}
    if name is not None:
        data["name"] = name
    if weight is not None:
        data["weight"] = float(weight)
    if data:
        supabase.table("aspects").update(data).eq("id", aspect_id).execute()
    return True


def delete_aspect(aspect_id: int) -> bool:
    supabase = get_supabase()
    supabase.table("aspects").delete().eq("id", aspect_id).execute()
    return True


# ===================================================================
# 1. CRUD Criteria
# ===================================================================
def get_all_criteria() -> list:
    supabase = get_supabase()
    resp = supabase.table("criteria").select("*").order("id").execute()
    return resp.data if resp.data else []


def get_criteria_by_id(criteria_id: int) -> dict:
    supabase = get_supabase()
    resp = supabase.table("criteria").select("*").eq("id", criteria_id).execute()
    if not resp.data:
        raise ValueError(f"Criteria dengan id {criteria_id} tidak ditemukan.")
    return resp.data[0]


def create_criteria(name: str, description: str = '') -> int:
    supabase = get_supabase()
    data = {"name": name}
    if description is not None:
        data["description"] = description
    resp = supabase.table("criteria").insert(data).execute()
    if not resp.data:
        raise ValueError(f"Kriteria dengan nama '{name}' sudah ada.")
    return resp.data[0]["id"]


def update_criteria(criteria_id: int, name: str = None, description: str = None) -> bool:
    supabase = get_supabase()
    data = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if data:
        supabase.table("criteria").update(data).eq("id", criteria_id).execute()
    return True


def delete_criteria(criteria_id: int) -> bool:
    supabase = get_supabase()
    supabase.table("criteria").delete().eq("id", criteria_id).execute()
    return True


# ===================================================================
# 2. CRUD Departments
# ===================================================================
def get_all_departments() -> list:
    supabase = get_supabase()
    resp = supabase.table("departments").select("*").order("id").execute()
    return resp.data if resp.data else []


def get_department_by_id(department_id: int) -> dict:
    supabase = get_supabase()
    resp = supabase.table("departments").select("*").eq("id", department_id).execute()
    if not resp.data:
        raise ValueError(f"Department dengan id {department_id} tidak ditemukan.")
    return resp.data[0]


def create_department(name: str) -> int:
    supabase = get_supabase()
    resp = supabase.table("departments").insert({"name": name}).execute()
    if not resp.data:
        raise ValueError(f"Department dengan nama '{name}' sudah ada.")
    return resp.data[0]["id"]


def update_department(department_id: int, name: str) -> bool:
    supabase = get_supabase()
    supabase.table("departments").update({"name": name}).eq("id", department_id).execute()
    return True


def delete_department(department_id: int) -> bool:
    supabase = get_supabase()
    supabase.table("departments").delete().eq("id", department_id).execute()
    return True


# ===================================================================
# 3. Department Profiles (dengan aspect_id)
# ===================================================================
def get_department_profiles(department_id: int, active_only: bool = False) -> list:
    supabase = get_supabase()
    query = (
        supabase.table("department_profiles")
        .select("*")
        .eq("department_id", department_id)
    )
    if active_only:
        query = query.eq("is_active", 1)
    resp = query.execute()
    if not resp.data:
        return []
    result = []
    for row in resp.data:
        # Ambil nama criteria dari tabel terpisah
        try:
            crit = supabase.table("criteria").select("name").eq("id", row["criteria_id"]).execute()
            row["criteria_name"] = crit.data[0]["name"] if crit.data else ""
        except Exception:
            row["criteria_name"] = ""
        # Ambil data aspek dari tabel terpisah (jika aspect_id ada)
        aspect_id = row.get("aspect_id")
        if aspect_id:
            try:
                asp = supabase.table("aspects").select("name, weight").eq("id", aspect_id).execute()
                if asp.data:
                    row["aspect_name"] = asp.data[0]["name"]
                    row["aspect_weight"] = asp.data[0]["weight"]
                else:
                    row["aspect_name"] = ""
                    row["aspect_weight"] = None
            except Exception:
                row["aspect_name"] = ""
                row["aspect_weight"] = None
        else:
            row["aspect_name"] = ""
            row["aspect_weight"] = None
        result.append(row)
    return result


def add_department_profile(
    department_id: int, criteria_id: int, target_value: float, weight: float, type_: str,
    aspect_id: int = None
) -> int:
    if type_ not in ("core", "secondary"):
        raise ValueError("type harus 'core' atau 'secondary'.")
    supabase = get_supabase()
    data = {
        "department_id": department_id,
        "criteria_id": criteria_id,
        "target_value": float(target_value),
        "weight": float(weight),
        "type": type_,
    }
    if aspect_id is not None:
        data["aspect_id"] = aspect_id
    resp = supabase.table("department_profiles").insert(data).execute()
    if not resp.data:
        raise ValueError("Gagal menambahkan profile.")
    return resp.data[0]["id"]


def update_department_profile(
    profile_id: int,
    target_value: float = None,
    weight: float = None,
    type_: str = None,
    is_active: int = None,
    aspect_id: int = None,
) -> bool:
    supabase = get_supabase()
    data = {}
    if target_value is not None:
        data["target_value"] = float(target_value)
    if weight is not None:
        data["weight"] = float(weight)
    if type_ is not None:
        if type_ not in ("core", "secondary"):
            raise ValueError("type harus 'core' atau 'secondary'.")
        data["type"] = type_
    if is_active is not None:
        data["is_active"] = int(is_active)
    if aspect_id is not None:
        data["aspect_id"] = aspect_id
    if data:
        supabase.table("department_profiles").update(data).eq("id", profile_id).execute()
    return True


def delete_department_profile(profile_id: int) -> bool:
    supabase = get_supabase()
    supabase.table("department_profiles").delete().eq("id", profile_id).execute()
    return True


def get_active_profiles(department_id: int) -> list:
    return get_department_profiles(department_id, active_only=True)


# ===================================================================
# 4. CRUD Alternatives
# ===================================================================
def get_all_alternatives() -> list:
    supabase = get_supabase()
    resp = supabase.table("alternatives").select("*").order("id").execute()
    return resp.data if resp.data else []


def get_alternative_by_id(alternative_id: int) -> dict:
    supabase = get_supabase()
    resp = supabase.table("alternatives").select("*").eq("id", alternative_id).execute()
    if not resp.data:
        raise ValueError(f"Alternative dengan id {alternative_id} tidak ditemukan.")
    return resp.data[0]


def create_alternative(
    name: str, nim: str, prodi: str, kelas: str, additional_info: str = ''
) -> int:
    supabase = get_supabase()
    data = {
        "name": name,
        "nim": nim,
        "prodi": prodi,
        "kelas": kelas,
    }
    if additional_info is not None:
        data["additional_info"] = additional_info
    resp = supabase.table("alternatives").insert(data).execute()
    if not resp.data:
        raise ValueError(f"Alternatif dengan nama '{name}' sudah ada.")
    return resp.data[0]["id"]


def update_alternative(
    alternative_id: int,
    name: str = None,
    nim: str = None,
    prodi: str = None,
    kelas: str = None,
    additional_info: str = '',
) -> bool:
    supabase = get_supabase()
    data = {}
    if name is not None:
        data["name"] = name
    if nim is not None:
        data["nim"] = nim
    if prodi is not None:
        data["prodi"] = prodi
    if kelas is not None:
        data["kelas"] = kelas
    if additional_info is not None:
        data["additional_info"] = additional_info
    if data:
        supabase.table("alternatives").update(data).eq("id", alternative_id).execute()
    return True


def delete_alternative(alternative_id: int) -> bool:
    supabase = get_supabase()
    supabase.table("alternatives").delete().eq("id", alternative_id).execute()
    return True


# ===================================================================
# 5. Alternative Scores
# ===================================================================
def get_alternative_scores(alternative_id: int) -> dict:
    supabase = get_supabase()
    resp = (
        supabase.table("alternative_scores")
        .select("criteria_id, value")
        .eq("alternative_id", alternative_id)
        .execute()
    )
    if not resp.data:
        return {}
    return {row["criteria_id"]: row["value"] for row in resp.data}


def set_alternative_score(alternative_id: int, criteria_id: int, value: float) -> int:
    supabase = get_supabase()
    value = float(value)
    existing = (
        supabase.table("alternative_scores")
        .select("id")
        .eq("alternative_id", alternative_id)
        .eq("criteria_id", criteria_id)
        .execute()
    )
    if existing.data:
        supabase.table("alternative_scores").update({"value": value}).eq(
            "alternative_id", alternative_id
        ).eq("criteria_id", criteria_id).execute()
        return existing.data[0]["id"]
    else:
        data = {
            "alternative_id": alternative_id,
            "criteria_id": criteria_id,
            "value": value,
        }
        resp = supabase.table("alternative_scores").insert(data).execute()
        return resp.data[0]["id"]


# ===================================================================
# 6. Department Rankings (Cache) - hanya total
# ===================================================================
def clear_department_rankings(department_id: int):
    supabase = get_supabase()
    supabase.table("department_rankings").delete().eq("department_id", department_id).execute()


def clear_all_rankings():
    supabase = get_supabase()
    supabase.table("department_rankings").delete().neq("id", 0).execute()


def save_department_ranking(department_id: int, rankings: list):
    supabase = get_supabase()
    clear_department_rankings(department_id)
    records = [
        {
            "department_id": department_id,
            "alternative_id": r["alternative_id"],
            "total": r["total"],
        }
        for r in rankings
    ]
    if records:
        supabase.table("department_rankings").insert(records).execute()


def get_cached_ranking(department_id: int) -> list:
    supabase = get_supabase()
    resp = (
        supabase.table("department_rankings")
        .select("*, alternatives!inner(name)")
        .eq("department_id", department_id)
        .order("total", desc=True)
        .execute()
    )
    if not resp.data:
        return []
    result = []
    for row in resp.data:
        row["alternative_name"] = row.pop("alternatives", {}).get("name", "")
        result.append(row)
    return result