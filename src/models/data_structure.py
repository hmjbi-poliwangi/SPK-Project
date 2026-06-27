import sqlite3
import os
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, '..', '..', 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')

# -------------------------------------------------------------------
# Koneksi database
# -------------------------------------------------------------------
def get_connection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@contextmanager
def get_db_read():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

# -------------------------------------------------------------------
# 1. CRUD Departments
# -------------------------------------------------------------------
def create_department(name: str) -> int:
    try:
        with get_db() as conn:
            cur = conn.execute("INSERT INTO departments (name) VALUES (?)", (name,))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Department dengan nama '{name}' sudah ada.")

def get_all_departments() -> list:
    with get_db_read() as conn:
        return conn.execute("SELECT * FROM departments ORDER BY id").fetchall()

def get_department_by_id(department_id: int) -> dict:
    with get_db_read() as conn:
        row = conn.execute("SELECT * FROM departments WHERE id = ?", (department_id,)).fetchone()
        if row is None:
            raise ValueError(f"Department dengan id {department_id} tidak ditemukan.")
        return row

def update_department(department_id: int, name: str) -> bool:
    try:
        with get_db() as conn:
            conn.execute("UPDATE departments SET name = ? WHERE id = ?", (name, department_id))
            return True
    except sqlite3.IntegrityError:
        raise ValueError(f"Nama '{name}' sudah dipakai departemen lain.")

def delete_department(department_id: int) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM departments WHERE id = ?", (department_id,))
        return True

# -------------------------------------------------------------------
# 2. CRUD Criteria
# -------------------------------------------------------------------
def create_criteria(name: str, description: str = None) -> int:
    try:
        with get_db() as conn:
            cur = conn.execute("INSERT INTO criteria (name, description) VALUES (?, ?)", (name, description))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Kriteria dengan nama '{name}' sudah ada.")

def get_all_criteria() -> list:
    with get_db_read() as conn:
        return conn.execute("SELECT * FROM criteria ORDER BY id").fetchall()

def get_criteria_by_id(criteria_id: int) -> dict:
    with get_db_read() as conn:
        row = conn.execute("SELECT * FROM criteria WHERE id = ?", (criteria_id,)).fetchone()
        if row is None:
            raise ValueError(f"Criteria dengan id {criteria_id} tidak ditemukan.")
        return row

def update_criteria(criteria_id: int, name: str = None, description: str = None) -> bool:
    try:
        with get_db() as conn:
            if name is not None:
                conn.execute("UPDATE criteria SET name = ? WHERE id = ?", (name, criteria_id))
            if description is not None:
                conn.execute("UPDATE criteria SET description = ? WHERE id = ?", (description, criteria_id))
            return True
    except sqlite3.IntegrityError:
        raise ValueError(f"Nama kriteria '{name}' sudah digunakan.")

def delete_criteria(criteria_id: int) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM criteria WHERE id = ?", (criteria_id,))
        return True

# -------------------------------------------------------------------
# 3. CRUD Alternatives (tanpa department_id)
# -------------------------------------------------------------------
def create_alternative(name: str, additional_info: str = None) -> int:
    """Tambah alternatif independen (tanpa departemen)."""
    try:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO alternatives (name, additional_info) VALUES (?, ?)",
                (name, additional_info)
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Alternatif dengan nama '{name}' sudah ada.")

def get_all_alternatives() -> list:
    """Ambil semua alternatif (tanpa info departemen)."""
    with get_db_read() as conn:
        return conn.execute("SELECT * FROM alternatives ORDER BY id").fetchall()

def get_alternative_by_id(alternative_id: int) -> dict:
    with get_db_read() as conn:
        row = conn.execute("SELECT * FROM alternatives WHERE id = ?", (alternative_id,)).fetchone()
        if row is None:
            raise ValueError(f"Alternative dengan id {alternative_id} tidak ditemukan.")
        return row

def update_alternative(alternative_id: int, name: str = None,
                       additional_info: str = None) -> bool:
    """Ubah data alternatif, tanpa departemen."""
    try:
        with get_db() as conn:
            if name is not None:
                conn.execute("UPDATE alternatives SET name = ? WHERE id = ?", (name, alternative_id))
            if additional_info is not None:
                conn.execute("UPDATE alternatives SET additional_info = ? WHERE id = ?", (additional_info, alternative_id))
            return True
    except sqlite3.IntegrityError:
        raise ValueError("Nama alternatif sudah ada.")

def delete_alternative(alternative_id: int) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM alternatives WHERE id = ?", (alternative_id,))
        return True

# -------------------------------------------------------------------
# 4. Department Profiles
# -------------------------------------------------------------------
def add_department_profile(department_id: int, criteria_id: int,
                           target_value: float, weight: float, type_: str) -> int:
    if type_ not in ('core', 'secondary'):
        raise ValueError("type harus 'core' atau 'secondary'.")
    try:
        target_value = float(target_value)
        weight = float(weight)
    except (ValueError, TypeError):
        raise ValueError("target_value dan weight harus berupa angka.")
    try:
        with get_db() as conn:
            cur = conn.execute("""
                INSERT INTO department_profiles (department_id, criteria_id, target_value, weight, type)
                VALUES (?, ?, ?, ?, ?)
            """, (department_id, criteria_id, target_value, weight, type_))
            return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Profil untuk kriteria tersebut sudah ada di departemen ini.")
        elif "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Department atau criteria id tidak valid.")
        else:
            raise

def update_department_profile(profile_id: int, target_value: float = None,
                              weight: float = None, type_: str = None,
                              is_active: int = None) -> bool:
    if target_value is not None:
        try:
            target_value = float(target_value)
        except (ValueError, TypeError):
            raise ValueError("target_value harus berupa angka.")
    if weight is not None:
        try:
            weight = float(weight)
        except (ValueError, TypeError):
            raise ValueError("weight harus berupa angka.")
    if type_ is not None and type_ not in ('core', 'secondary'):
        raise ValueError("type harus 'core' atau 'secondary'.")
    if is_active is not None and is_active not in (0, 1):
        raise ValueError("is_active harus 0 atau 1.")

    with get_db() as conn:
        if target_value is not None:
            conn.execute("UPDATE department_profiles SET target_value = ? WHERE id = ?", (target_value, profile_id))
        if weight is not None:
            conn.execute("UPDATE department_profiles SET weight = ? WHERE id = ?", (weight, profile_id))
        if type_ is not None:
            conn.execute("UPDATE department_profiles SET type = ? WHERE id = ?", (type_, profile_id))
        if is_active is not None:
            conn.execute("UPDATE department_profiles SET is_active = ? WHERE id = ?", (is_active, profile_id))
        return True

def delete_department_profile(profile_id: int) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM department_profiles WHERE id = ?", (profile_id,))
        return True

def get_department_profiles(department_id: int, active_only: bool = False) -> list:
    with get_db_read() as conn:
        if active_only:
            return conn.execute("""
                SELECT dp.*, c.name as criteria_name
                FROM department_profiles dp
                JOIN criteria c ON dp.criteria_id = c.id
                WHERE dp.department_id = ? AND dp.is_active = 1
            """, (department_id,)).fetchall()
        else:
            return conn.execute("""
                SELECT dp.*, c.name as criteria_name
                FROM department_profiles dp
                JOIN criteria c ON dp.criteria_id = c.id
                WHERE dp.department_id = ?
            """, (department_id,)).fetchall()

def get_active_profiles(department_id):
    return get_department_profiles(department_id, active_only=True)

# -------------------------------------------------------------------
# 5. Alternative Scores
# -------------------------------------------------------------------
def set_alternative_score(alternative_id: int, criteria_id: int, value: float) -> int:
    try:
        value = float(value)
    except (ValueError, TypeError):
        raise ValueError("Nilai harus berupa angka.")
    try:
        with get_db() as conn:
            cur = conn.execute("""
                INSERT INTO alternative_scores (alternative_id, criteria_id, value)
                VALUES (?, ?, ?)
            """, (alternative_id, criteria_id, value))
            return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            with get_db() as conn:
                conn.execute("""
                    UPDATE alternative_scores SET value = ? WHERE alternative_id = ? AND criteria_id = ?
                """, (value, alternative_id, criteria_id))
                row = conn.execute("SELECT id FROM alternative_scores WHERE alternative_id = ? AND criteria_id = ?",
                                   (alternative_id, criteria_id)).fetchone()
                return row['id'] if row else None
        elif "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Alternative atau criteria id tidak valid.")
        else:
            raise

def update_alternative_score(score_id: int, value: float) -> bool:
    try:
        value = float(value)
    except (ValueError, TypeError):
        raise ValueError("Nilai harus berupa angka.")
    with get_db() as conn:
        conn.execute("UPDATE alternative_scores SET value = ? WHERE id = ?", (value, score_id))
        return True

def delete_alternative_score(score_id: int) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM alternative_scores WHERE id = ?", (score_id,))
        return True

def get_alternative_scores(alternative_id: int) -> dict:
    with get_db_read() as conn:
        rows = conn.execute("""
            SELECT criteria_id, value FROM alternative_scores
            WHERE alternative_id = ?
        """, (alternative_id,)).fetchall()
        return {row['criteria_id']: row['value'] for row in rows}

# -------------------------------------------------------------------
# 6. Tabel cache department_rankings
# -------------------------------------------------------------------
def clear_department_rankings(department_id: int):
    """Hapus cache peringkat untuk satu departemen."""
    with get_db() as conn:
        conn.execute("DELETE FROM department_rankings WHERE department_id = ?", (department_id,))

def clear_all_rankings():
    """Hapus seluruh cache peringkat (semua departemen)."""
    with get_db() as conn:
        conn.execute("DELETE FROM department_rankings")

def save_department_ranking(department_id: int, rankings: list):
    """Simpan hasil peringkat ke cache (list of dict dengan keys: alternative_id, ncf, nsf, total)."""
    with get_db() as conn:
        for r in rankings:
            conn.execute("""
                INSERT INTO department_rankings (department_id, alternative_id, ncf, nsf, total)
                VALUES (?, ?, ?, ?, ?)
            """, (department_id, r['alternative_id'], r['ncf'], r['nsf'], r['total']))

def get_cached_ranking(department_id: int) -> list:
    """Ambil peringkat dari cache (diurutkan total desc)."""
    with get_db_read() as conn:
        rows = conn.execute("""
            SELECT dr.*, a.name as alternative_name
            FROM department_rankings dr
            JOIN alternatives a ON dr.alternative_id = a.id
            WHERE dr.department_id = ?
            ORDER BY dr.total DESC
        """, (department_id,)).fetchall()
        return [dict(row) for row in rows]

# -------------------------------------------------------------------
# Pembuatan tabel
# -------------------------------------------------------------------
def create_tables():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS criteria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS department_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_id INTEGER NOT NULL,
                criteria_id INTEGER NOT NULL,
                target_value REAL NOT NULL,
                weight REAL NOT NULL DEFAULT 0,
                type TEXT NOT NULL CHECK(type IN ('core', 'secondary')),
                is_active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
                FOREIGN KEY (criteria_id) REFERENCES criteria(id) ON DELETE CASCADE,
                UNIQUE(department_id, criteria_id)
            );

            CREATE TABLE IF NOT EXISTS alternatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                additional_info TEXT
            );

            CREATE TABLE IF NOT EXISTS alternative_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alternative_id INTEGER NOT NULL,
                criteria_id INTEGER NOT NULL,
                value REAL NOT NULL,
                FOREIGN KEY (alternative_id) REFERENCES alternatives(id) ON DELETE CASCADE,
                FOREIGN KEY (criteria_id) REFERENCES criteria(id) ON DELETE CASCADE,
                UNIQUE(alternative_id, criteria_id)
            );

            CREATE TABLE IF NOT EXISTS department_rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_id INTEGER NOT NULL,
                alternative_id INTEGER NOT NULL,
                ncf REAL NOT NULL,
                nsf REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
                FOREIGN KEY (alternative_id) REFERENCES alternatives(id) ON DELETE CASCADE,
                UNIQUE(department_id, alternative_id)
            );

            CREATE INDEX IF NOT EXISTS idx_dept_profiles_dept ON department_profiles(department_id);
            CREATE INDEX IF NOT EXISTS idx_dept_profiles_criteria ON department_profiles(criteria_id);
            CREATE INDEX IF NOT EXISTS idx_alt_scores_alt ON alternative_scores(alternative_id);
            CREATE INDEX IF NOT EXISTS idx_alt_scores_criteria ON alternative_scores(criteria_id);
            CREATE INDEX IF NOT EXISTS idx_dept_rankings_dept ON department_rankings(department_id);
        """)