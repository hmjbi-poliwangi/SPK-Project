# SPK Profile Matching

Sistem Pendukung Keputusan (SPK) untuk perankingan kandidat/mahasiswa ke departemen 
berdasarkan kriteria menggunakan metode Profile Matching.

## Fitur

- Manajemen Kriteria, Departemen, Aspek, Alternatif
- Perankingan otomatis dengan metode Profile Matching
- Export PDF & JSON
- Import data dari JSON
- Responsive design (mobile & desktop)

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** Supabase (PostgreSQL)
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Deployment:** Vercel
- **PDF Generation:** ReportLab

## Prerequisites

- Python 3.9+
- Node.js (untuk Vercel CLI, opsional)
- Akun Supabase (gratis)

## Setup Lokal

### 1. Clone Repository
```bash
git clone https://github.com/username/SPK-Project.git
cd SPK-Project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Supabase

1. Buat project di https://supabase.com
2. Buka **SQL Editor** → **New Query**
3. Copy paste SQL dari `CREATE_TABLES_SQL` di `src/models/supabase_db.py`
4. Klik **Run**

### 4. Setup Environment Variables

Buat file `.env` di root project:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here
```

**Cara mendapatkan SUPABASE_URL dan SUPABASE_KEY:**
- Buka Supabase Dashboard → **Settings** → **API**
- **Project URL** → copy untuk `SUPABASE_URL`
- **anon public** key → copy untuk `SUPABASE_KEY`

### 5. Jalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## Deploy ke Vercel

### 1. Push ke GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Import ke Vercel
1. Buka https://vercel.com
2. Klik **Add New** → **Project**
3. Import repository GitHub
4. Framework Preset: **Python**

### 3. Set Environment Variables
Di Vercel Dashboard → **Settings** → **Environment Variables**:
- `SUPABASE_URL` → URL project Supabase
- `SUPABASE_KEY` → anon public key

### 4. Deploy
Klik **Deploy** dan tunggu sampai selesai.

## Project Structure

```
SPK-Project/
├── app.py                  # Entry point Web (Flask)
├── main_desktop.py         # Entry point Desktop (PySide6)
├── requirements.txt        # Dependencies
├── vercel.json             # Konfigurasi Vercel
├── .env.example            # Template environment variables
├── src/
│   ├── engine/             # Logika Profile Matching
│   ├── models/             # Database layer (Supabase & SQLite)
│   ├── utils/              # Export PDF & JSON
│   └── views/              # UI Desktop (PySide6)
├── templates/              # HTML templates
└── static/                 # CSS & JS
```

## API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/criteria` | Ambil semua kriteria |
| POST | `/api/criteria` | Tambah kriteria |
| GET | `/api/departments` | Ambil semua departemen |
| GET | `/api/departments/<id>/ranking` | Ambil ranking per departemen |
| GET | `/api/export/json` | Export data ke JSON |
| GET | `/api/export/pdf` | Export laporan ke PDF |

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `SUPABASE_URL not set` | Pastikan `.env` sudah dibuat dan diisi |
| Tabel belum dibuat | Jalankan SQL via Supabase SQL Editor |
| 500 Internal Server Error | Cek log di Vercel Dashboard |
