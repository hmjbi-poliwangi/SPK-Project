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
    """Buat koneksi baru dengan timeout untuk menghindari lock."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH, timeout=10)   # tunggu hingga 10 detik jika terkunci
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_db():
    """Context manager yang menjamin koneksi selalu ditutup dan commit/rollback otomatis."""
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
    """Context manager untuk operasi baca (tanpa commit)."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

# -------------------------------------------------------------------
# 1. CRUD Departments
# -------------------------------------------------------------------
def create_department(name: str) -> int:
    """Tambah departemen baru, kembalikan id."""
    try:
        with get_db() as conn:
            cur = conn.execute("INSERT INTO departments (name) VALUES (?)", (name,))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Department dengan nama '{name}' sudah ada.")

def get_all_departments() -> list:
    """Ambil semua departemen."""
    with get_db_read() as conn:
        return conn.execute("SELECT * FROM departments ORDER BY id").fetchall()

def get_department_by_id(department_id: int) -> dict:
    """Ambil satu departemen berdasarkan ID."""
    with get_db_read() as conn:
        row = conn.execute("SELECT * FROM departments WHERE id = ?", (department_id,)).fetchone()
        if row is None:
            raise ValueError(f"Department dengan id {department_id} tidak ditemukan.")
        return row

def update_department(department_id: int, name: str) -> bool:
    """Ubah nama departemen."""
    try:
        with get_db() as conn:
            conn.execute("UPDATE departments SET name = ? WHERE id = ?", (name, department_id))
            return True
    except sqlite3.IntegrityError:
        raise ValueError(f"Nama '{name}' sudah dipakai departemen lain.")

def delete_department(department_id: int) -> bool:
    """Hapus departemen (cascade ke profiles & alternatives)."""
    with get_db() as conn:
        conn.execute("DELETE FROM departments WHERE id = ?", (department_id,))
        return True

# -------------------------------------------------------------------
# 2. CRUD Criteria
# -------------------------------------------------------------------
def create_criteria(name: str, description: str = None) -> int:
    """Tambah kriteria baru."""
    try:
        with get_db() as conn:
            cur = conn.execute("INSERT INTO criteria (name, description) VALUES (?, ?)", (name, description))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Kriteria dengan nama '{name}' sudah ada.")

def get_all_criteria() -> list:
    """Ambil semua kriteria."""
    with get_db_read() as conn:
        return conn.execute("SELECT * FROM criteria ORDER BY id").fetchall()

def get_criteria_by_id(criteria_id: int) -> dict:
    """Ambil satu kriteria."""
    with get_db_read() as conn:
        row = conn.execute("SELECT * FROM criteria WHERE id = ?", (criteria_id,)).fetchone()
        if row is None:
            raise ValueError(f"Criteria dengan id {criteria_id} tidak ditemukan.")
        return row

def update_criteria(criteria_id: int, name: str = None, description: str = None) -> bool:
    """Ubah nama / deskripsi kriteria. Parameter yang None tidak diubah."""
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
    """Hapus kriteria (cascade ke profiles & scores)."""
    with get_db() as conn:
        conn.execute("DELETE FROM criteria WHERE id = ?", (criteria_id,))
        return True

# -------------------------------------------------------------------
# 3. CRUD Alternatives (kandidat)
# -------------------------------------------------------------------
def create_alternative(name: str, department_id: int, additional_info: str = None) -> int:
    """Tambah kandidat di suatu departemen."""
    try:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO alternatives (name, department_id, additional_info) VALUES (?, ?, ?)",
                (name, department_id, additional_info)
            )
            return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError(f"Kandidat '{name}' sudah ada di departemen tersebut.")
        elif "FOREIGN KEY constraint failed" in str(e):
            raise ValueError(f"Department dengan id {department_id} tidak ditemukan.")
        else:
            raise

def get_all_alternatives() -> list:
    """Ambil semua kandidat, sertakan nama departemen."""
    with get_db_read() as conn:
        return conn.execute("""
            SELECT a.*, d.name as department_name
            FROM alternatives a
            JOIN departments d ON a.department_id = d.id
            ORDER BY a.id
        """).fetchall()

def get_department_alternatives(department_id: int) -> list:
    """Semua kandidat di departemen tertentu."""
    with get_db_read() as conn:
        return conn.execute("SELECT * FROM alternatives WHERE department_id = ?", (department_id,)).fetchall()

# Alias untuk kompatibilitas mundur (jika ada yang memanggil get_alternatives_by_department)
def get_alternatives_by_department(department_id: int) -> list:
    """Alias dari get_department_alternatives."""
    return get_department_alternatives(department_id)

def get_alternative_by_id(alternative_id: int) -> dict:
    """Ambil satu kandidat beserta nama departemen."""
    with get_db_read() as conn:
        row = conn.execute("""
            SELECT a.*, d.name as department_name
            FROM alternatives a
            JOIN departments d ON a.department_id = d.id
            WHERE a.id = ?
        """, (alternative_id,)).fetchone()
        if row is None:
            raise ValueError(f"Alternative dengan id {alternative_id} tidak ditemukan.")
        return row

def update_alternative(alternative_id: int, name: str = None,
                       department_id: int = None, additional_info: str = None) -> bool:
    """Ubah data kandidat."""
    try:
        with get_db() as conn:
            if name is not None:
                conn.execute("UPDATE alternatives SET name = ? WHERE id = ?", (name, alternative_id))
            if department_id is not None:
                conn.execute("UPDATE alternatives SET department_id = ? WHERE id = ?", (department_id, alternative_id))
            if additional_info is not None:
                conn.execute("UPDATE alternatives SET additional_info = ? WHERE id = ?", (additional_info, alternative_id))
            return True
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Nama kandidat sudah ada di departemen tersebut.")
        elif "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Department id tidak valid.")
        else:
            raise

def delete_alternative(alternative_id: int) -> bool:
    """Hapus kandidat (cascade ke scores)."""
    with get_db() as conn:
        conn.execute("DELETE FROM alternatives WHERE id = ?", (alternative_id,))
        return True

# -------------------------------------------------------------------
# 4. Pengelolaan Department Profiles (relasi kriteria-departemen)
# -------------------------------------------------------------------
def add_department_profile(department_id: int, criteria_id: int,
                           target_value: float, weight: float, type_: str) -> int:
    """Tambahkan profil (bobot, target) kriteria untuk suatu departemen."""
    if type_ not in ('core', 'secondary'):
        raise ValueError("type harus 'core' atau 'secondary'.")
    # Validasi numerik
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
    """Ubah nilai pada profil yang sudah ada."""
    # Validasi
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
    """Hapus profil kriteria dari departemen."""
    with get_db() as conn:
        conn.execute("DELETE FROM department_profiles WHERE id = ?", (profile_id,))
        return True

def get_department_profiles(department_id: int, active_only: bool = False) -> list:
    """Ambil daftar profil untuk departemen, bisa filter yang aktif saja."""
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

# -------------------------------------------------------------------
# 5. Pengelolaan Alternative Scores (nilai kandidat per kriteria)
# -------------------------------------------------------------------
def set_alternative_score(alternative_id: int, criteria_id: int, value: float) -> int:
    """Set nilai kandidat untuk suatu kriteria (insert atau update otomatis)."""
    try:
        value = float(value)
    except (ValueError, TypeError):
        raise ValueError("Nilai harus berupa angka.")
    try:
        with get_db() as conn:
            # Coba insert
            cur = conn.execute("""
                INSERT INTO alternative_scores (alternative_id, criteria_id, value)
                VALUES (?, ?, ?)
            """, (alternative_id, criteria_id, value))
            return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            # Sudah ada, lakukan update
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
    """Update nilai berdasarkan id score."""
    try:
        value = float(value)
    except (ValueError, TypeError):
        raise ValueError("Nilai harus berupa angka.")
    with get_db() as conn:
        conn.execute("UPDATE alternative_scores SET value = ? WHERE id = ?", (value, score_id))
        return True

def delete_alternative_score(score_id: int) -> bool:
    """Hapus nilai berdasarkan id score."""
    with get_db() as conn:
        conn.execute("DELETE FROM alternative_scores WHERE id = ?", (score_id,))
        return True

def get_alternative_scores(alternative_id: int) -> dict:
    """Ambil semua nilai kandidat sebagai dict {criteria_id: value}."""
    with get_db_read() as conn:
        rows = conn.execute("""
            SELECT criteria_id, value FROM alternative_scores
            WHERE alternative_id = ?
        """, (alternative_id,)).fetchall()
        return {row['criteria_id']: row['value'] for row in rows}

# -------------------------------------------------------------------
# Pembuatan tabel (panggil saat inisialisasi aplikasi)
# -------------------------------------------------------------------
def create_tables():
    """Buat semua tabel dan indeks jika belum ada."""
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
                name TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                additional_info TEXT,
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
                UNIQUE(name, department_id)
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

            CREATE INDEX IF NOT EXISTS idx_dept_profiles_dept ON department_profiles(department_id);
            CREATE INDEX IF NOT EXISTS idx_dept_profiles_criteria ON department_profiles(criteria_id);
            CREATE INDEX IF NOT EXISTS idx_alternatives_dept ON alternatives(department_id);
            CREATE INDEX IF NOT EXISTS idx_alt_scores_alt ON alternative_scores(alternative_id);
            CREATE INDEX IF NOT EXISTS idx_alt_scores_criteria ON alternative_scores(criteria_id);
        """)