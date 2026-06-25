import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, '..', '..', 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')

def get_connection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# -------------------------------------------------------------------
# 1. CRUD Departments
# -------------------------------------------------------------------
def create_department(name: str) -> int:
    """Tambah departemen baru, kembalikan id."""
    conn = get_connection()
    try:
        cur = conn.execute("INSERT INTO departments (name) VALUES (?)", (name,))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Department dengan nama '{name}' sudah ada.")
    finally:
        conn.close()

def get_all_departments() -> list:
    """Ambil semua departemen."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM departments ORDER BY id").fetchall()
    conn.close()
    return rows

def get_department_by_id(department_id: int) -> dict:
    """Ambil satu departemen berdasarkan ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM departments WHERE id = ?", (department_id,)).fetchone()
    conn.close()
    if row is None:
        raise ValueError(f"Department dengan id {department_id} tidak ditemukan.")
    return row

def update_department(department_id: int, name: str) -> bool:
    """Ubah nama departemen."""
    conn = get_connection()
    try:
        conn.execute("UPDATE departments SET name = ? WHERE id = ?", (name, department_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise ValueError(f"Nama '{name}' sudah dipakai departemen lain.")
    finally:
        conn.close()

def delete_department(department_id: int) -> bool:
    """Hapus departemen (cascade ke profiles & alternatives)."""
    conn = get_connection()
    conn.execute("DELETE FROM departments WHERE id = ?", (department_id,))
    conn.commit()
    conn.close()
    return True

# -------------------------------------------------------------------
# 2. CRUD Criteria
# -------------------------------------------------------------------
def create_criteria(name: str, description: str = None) -> int:
    """Tambah kriteria baru."""
    conn = get_connection()
    try:
        cur = conn.execute("INSERT INTO criteria (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Kriteria dengan nama '{name}' sudah ada.")
    finally:
        conn.close()

def get_all_criteria() -> list:
    """Ambil semua kriteria."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM criteria ORDER BY id").fetchall()
    conn.close()
    return rows

def get_criteria_by_id(criteria_id: int) -> dict:
    """Ambil satu kriteria."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM criteria WHERE id = ?", (criteria_id,)).fetchone()
    conn.close()
    if row is None:
        raise ValueError(f"Criteria dengan id {criteria_id} tidak ditemukan.")
    return row

def update_criteria(criteria_id: int, name: str = None, description: str = None) -> bool:
    """Ubah nama / deskripsi kriteria. Parameter yang None tidak diubah."""
    conn = get_connection()
    try:
        if name is not None:
            conn.execute("UPDATE criteria SET name = ? WHERE id = ?", (name, criteria_id))
        if description is not None:
            conn.execute("UPDATE criteria SET description = ? WHERE id = ?", (description, criteria_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise ValueError(f"Nama kriteria '{name}' sudah digunakan.")
    finally:
        conn.close()

def delete_criteria(criteria_id: int) -> bool:
    """Hapus kriteria (cascade ke profiles & scores)."""
    conn = get_connection()
    conn.execute("DELETE FROM criteria WHERE id = ?", (criteria_id,))
    conn.commit()
    conn.close()
    return True

# -------------------------------------------------------------------
# 3. CRUD Alternatives (kandidat)
# -------------------------------------------------------------------
def create_alternative(name: str, department_id: int, additional_info: str = None) -> int:
    """Tambah kandidat di suatu departemen."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO alternatives (name, department_id, additional_info) VALUES (?, ?, ?)",
            (name, department_id, additional_info)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        # Bisa karena UNIQUE(name, department_id) atau foreign key department_id tidak ada
        if "UNIQUE constraint failed" in str(e):
            raise ValueError(f"Kandidat '{name}' sudah ada di departemen tersebut.")
        elif "FOREIGN KEY constraint failed" in str(e):
            raise ValueError(f"Department dengan id {department_id} tidak ditemukan.")
        else:
            raise
    finally:
        conn.close()

def get_all_alternatives() -> list:
    """Ambil semua kandidat, sertakan nama departemen."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*, d.name as department_name
        FROM alternatives a
        JOIN departments d ON a.department_id = d.id
        ORDER BY a.id
    """).fetchall()
    conn.close()
    return rows

def get_alternatives_by_department(department_id: int) -> list:
    """Ambil kandidat untuk departemen tertentu (fungsi asli bisa dipakai)."""
    # Sudah ada get_department_alternatives, tapi kita buat satu lagi yang konsisten
    conn = get_connection()
    rows = conn.execute("SELECT * FROM alternatives WHERE department_id = ?", (department_id,)).fetchall()
    conn.close()
    return rows

def get_alternative_by_id(alternative_id: int) -> dict:
    """Ambil satu kandidat."""
    conn = get_connection()
    row = conn.execute("""
        SELECT a.*, d.name as department_name
        FROM alternatives a
        JOIN departments d ON a.department_id = d.id
        WHERE a.id = ?
    """, (alternative_id,)).fetchone()
    conn.close()
    if row is None:
        raise ValueError(f"Alternative dengan id {alternative_id} tidak ditemukan.")
    return row

def update_alternative(alternative_id: int, name: str = None,
                       department_id: int = None, additional_info: str = None) -> bool:
    """Ubah data kandidat."""
    conn = get_connection()
    try:
        if name is not None:
            conn.execute("UPDATE alternatives SET name = ? WHERE id = ?", (name, alternative_id))
        if department_id is not None:
            conn.execute("UPDATE alternatives SET department_id = ? WHERE id = ?", (department_id, alternative_id))
        if additional_info is not None:
            conn.execute("UPDATE alternatives SET additional_info = ? WHERE id = ?", (additional_info, alternative_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Nama kandidat sudah ada di departemen tersebut.")
        elif "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Department id tidak valid.")
        else:
            raise
    finally:
        conn.close()

def delete_alternative(alternative_id: int) -> bool:
    """Hapus kandidat (cascade ke scores)."""
    conn = get_connection()
    conn.execute("DELETE FROM alternatives WHERE id = ?", (alternative_id,))
    conn.commit()
    conn.close()
    return True

# -------------------------------------------------------------------
# 4. Pengelolaan Department Profiles (relasi kriteria-departemen)
# -------------------------------------------------------------------
def add_department_profile(department_id: int, criteria_id: int,
                           target_value: float, weight: float, type_: str) -> int:
    """Tambahkan profil (bobot, target) kriteria untuk suatu departemen."""
    if type_ not in ('core', 'secondary'):
        raise ValueError("type harus 'core' atau 'secondary'.")
    conn = get_connection()
    try:
        cur = conn.execute("""
            INSERT INTO department_profiles (department_id, criteria_id, target_value, weight, type)
            VALUES (?, ?, ?, ?, ?)
        """, (department_id, criteria_id, target_value, weight, type_))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Profil untuk kriteria tersebut sudah ada di departemen ini.")
        elif "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Department atau criteria id tidak valid.")
        else:
            raise
    finally:
        conn.close()

def update_department_profile(profile_id: int, target_value: float = None,
                              weight: float = None, type_: str = None,
                              is_active: int = None) -> bool:
    """Ubah nilai pada profil yang sudah ada."""
    conn = get_connection()
    if target_value is not None:
        conn.execute("UPDATE department_profiles SET target_value = ? WHERE id = ?", (target_value, profile_id))
    if weight is not None:
        conn.execute("UPDATE department_profiles SET weight = ? WHERE id = ?", (weight, profile_id))
    if type_ is not None:
        if type_ not in ('core', 'secondary'):
            raise ValueError("type harus 'core' atau 'secondary'.")
        conn.execute("UPDATE department_profiles SET type = ? WHERE id = ?", (type_, profile_id))
    if is_active is not None:
        conn.execute("UPDATE department_profiles SET is_active = ? WHERE id = ?", (is_active, profile_id))
    conn.commit()
    conn.close()
    return True

def delete_department_profile(profile_id: int) -> bool:
    """Hapus profil kriteria dari departemen."""
    conn = get_connection()
    conn.execute("DELETE FROM department_profiles WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()
    return True

def get_department_profiles(department_id: int, active_only: bool = False) -> list:
    """Ambil daftar profil untuk departemen, bisa filter yang aktif saja."""
    conn = get_connection()
    if active_only:
        rows = conn.execute("""
            SELECT dp.*, c.name as criteria_name
            FROM department_profiles dp
            JOIN criteria c ON dp.criteria_id = c.id
            WHERE dp.department_id = ? AND dp.is_active = 1
        """, (department_id,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT dp.*, c.name as criteria_name
            FROM department_profiles dp
            JOIN criteria c ON dp.criteria_id = c.id
            WHERE dp.department_id = ?
        """, (department_id,)).fetchall()
    conn.close()
    return rows

# -------------------------------------------------------------------
# 5. Pengelolaan Alternative Scores (nilai kandidat per kriteria)
# -------------------------------------------------------------------
def set_alternative_score(alternative_id: int, criteria_id: int, value: float) -> int:
    """Set nilai kandidat untuk suatu kriteria (insert atau replace)."""
    conn = get_connection()
    try:
        # Coba insert dulu
        cur = conn.execute("""
            INSERT INTO alternative_scores (alternative_id, criteria_id, value)
            VALUES (?, ?, ?)
        """, (alternative_id, criteria_id, value))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            # Sudah ada -> update
            conn.execute("""
                UPDATE alternative_scores SET value = ? WHERE alternative_id = ? AND criteria_id = ?
            """, (value, alternative_id, criteria_id))
            conn.commit()
            # Dapatkan id-nya
            row = conn.execute("SELECT id FROM alternative_scores WHERE alternative_id = ? AND criteria_id = ?",
                               (alternative_id, criteria_id)).fetchone()
            conn.close()
            return row['id']
        elif "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Alternative atau criteria id tidak valid.")
        else:
            raise
    finally:
        conn.close()

def update_alternative_score(score_id: int, value: float) -> bool:
    """Update nilai berdasarkan id score."""
    conn = get_connection()
    conn.execute("UPDATE alternative_scores SET value = ? WHERE id = ?", (value, score_id))
    conn.commit()
    conn.close()
    return True

def delete_alternative_score(score_id: int) -> bool:
    """Hapus nilai berdasarkan id score."""
    conn = get_connection()
    conn.execute("DELETE FROM alternative_scores WHERE id = ?", (score_id,))
    conn.commit()
    conn.close()
    return True

def get_alternative_scores_dict(alternative_id: int) -> dict:
    """Ambil semua nilai kandidat sebagai dict {criteria_id: value} (fungsi asli)."""
    # Gunakan fungsi yang sudah ada
    return get_alternative_scores(alternative_id)   # fungsi asli di bawah

# (Pastikan fungsi get_alternative_scores asli tetap tersedia)
def get_alternative_scores(alternative_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT criteria_id, value FROM alternative_scores
        WHERE alternative_id = ?
    """, (alternative_id,))
    scores = {row['criteria_id']: row['value'] for row in cursor.fetchall()}
    conn.close()
    return scores

# -------------------------------------------------------------------
# Buat tabel jika diperlukan (opsional saat import, bisa dipanggil manual)
# -------------------------------------------------------------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
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
    conn.commit()
    conn.close()

# -------------------------------------------------------------------
# Demo / __main__
# -------------------------------------------------------------------
if __name__ == "__main__":
    create_tables()

    # --- Contoh penggunaan CRUD ---
    # 1. Departemen
    dept_id = create_department("IT")
    print("Department created:", dept_id)
    update_department(dept_id, "Teknologi Informasi")
    print(get_department_by_id(dept_id)['name'])

    # 2. Kriteria
    crit_id = create_criteria("Pengalaman Kerja", "Lama pengalaman dalam tahun")
    print("Criteria created:", crit_id)

    # 3. Profil (bobot & target)
    prof_id = add_department_profile(dept_id, crit_id, target_value=5.0, weight=0.3, type_='core')
    print("Profile created:", prof_id)

    # 4. Kandidat
    alt_id = create_alternative("Andi", dept_id, "S1 Informatika")
    print("Alternative created:", alt_id)

    # 5. Nilai kandidat
    set_alternative_score(alt_id, crit_id, 4.5)
    print("Scores:", get_alternative_scores(alt_id))

    # 6. Hapus semua (cascade)
    delete_alternative(alt_id)
    delete_criteria(crit_id)
    delete_department(dept_id)
    print("Data dibersihkan.")