import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, '..', '..', 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')

def get_connection():
    # Pastikan folder data ada
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

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

def get_active_profiles(department_id):
    """Mengembalikan daftar profil kriteria yang aktif untuk suatu departemen."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dp.id, dp.criteria_id, c.name, dp.target_value, dp.weight, dp.type
        FROM department_profiles dp
        JOIN criteria c ON dp.criteria_id = c.id
        WHERE dp.department_id = ? AND dp.is_active = 1
    """, (department_id,))
    profiles = cursor.fetchall()
    conn.close()
    return profiles

def get_alternative_scores(alternative_id):
    """Nilai mentah seorang kandidat untuk semua kriteria yang dinilai."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT criteria_id, value FROM alternative_scores
        WHERE alternative_id = ?
    """, (alternative_id,))
    scores = {row['criteria_id']: row['value'] for row in cursor.fetchall()}
    conn.close()
    return scores

def get_department_alternatives(department_id):
    """Semua kandidat di departemen tertentu."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alternatives WHERE department_id = ?", (department_id,))
    alts = cursor.fetchall()
    conn.close()
    return alts

if __name__ == "__main__":
    create_tables()