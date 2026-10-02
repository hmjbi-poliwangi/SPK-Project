# Penjelasan Algoritma SPK Profile Matching

Dokumen ini menjelaskan cara kerja perhitungan pada aplikasi SPK (Sistem Pendukung Keputusan) ini secara **lengkap namun sederhana** — menggunakan bahasa sehari-hari, dengan contoh angka, sehingga siapa pun bisa memahaminya tanpa harus paham pemrograman.

---

## 1. Ini Aplikasi Apa Sih?

Aplikasi ini adalah **"pembantu pengambil keputusan"** untuk memilih orang yang paling cocok ditempatkan atau diterima pada sebuah **posisi/bagian** (di aplikasi ini disebut **Departemen**).

Cara kerjanya meniru cara rekrutmen sungguhan:

1. Kita tentukan dulu **"profil orang seperti apa yang kita cari"** untuk setiap departemen,
2. Lalu kita **bandingkan satu per satu** profil para calon (di aplikasi ini disebut **Alternatif**),
3. Terakhir kita hitung **siapa yang paling mendekati profil yang dicari**, lalu urutkan.

Mencocokkan profil inilah yang disebut **Profile Matching** ("pencocokan profil").

> Catatan kecil: aplikasi ini hadir dalam dua bentuk — **versi internet** (agar bisa diakses banyak orang lewat peramban) dan **versi program di komputer** (untuk pemakaian pribadi). Keduanya memakai cara hitung yang **persis sama**.

---

## 2. Alur SPK Secara Umum (Gambaran Besar)

Perjalanan data dari awal sampai munculnya peringkat:

**Tahap 1 — Menentukan "apa yang dinilai" (Kriteria)**
Buat daftar hal-hal yang ingin dinilai dari calon, misalnya: IPK, Tes Kemampuan, Kedisiplinan, Kerja Sama, dan sebagainya.

**Tahap 2 — Mengelompokkan kriteria ke dalam "Aspek"**
Kriteria-kriteria yang sejenis digabung ke dalam satu kelompok agar hasilnya lebih mudah dipahami, misalnya kelompok "Intelektual" dan kelompok "Sikap".

**Tahap 3 — Menentukan "profil yang dicari" untuk tiap Departemen**
Untuk setiap departemen, tentukan **nilai ideal** tiap kriteria (nilai 0–5), atribut **bobot** kriteria (disimpan, namun tidak lagi dipakai dalam hitungan), dan apakah kriteria itu tergolong **inti** (utama) atau **pendukung**.

**Tahap 4 — Mencatat "profil yang dimiliki" setiap calon**
Catat nilai yang dimiliki setiap calon pada tiap kriteria (juga berskala 0–5).

**Tahap 5 — Menghitung kecocokan**
Untuk setiap calon pada setiap departemen:
- hitung **selisih** antara nilai calon dan nilai ideal,
- ubah selisih itu menjadi **skor kecocokan**,
- gabungkan skor dalam tiap aspek (kelompok inti & pendukung),
- gabungkan semua aspek menjadi **satu nilai akhir**.

**Tahap 6 — Mengurutkan dan menyajikan hasil**
Urutkan calon dari nilai akhir tertinggi ke terendah → itulah **peringkat**. Hasilnya bisa dilihat di layar maupun disimpan dalam bentuk laporan.

Intinya sederhana: **siapa yang paling cocok → dialah pemenangnya.** Semakin tinggi nilai akhir, semakin cocok orang itu dengan posisi yang dicari.

---

## 3. Penjelasan Lengkap Setiap Tahap

### 3.1 Kriteria — "Apa yang dinilai?"

Kriteria adalah **hal-hal yang menjadi bahan penilaian** terhadap calon. Contoh:

| Kriteria | Maksudnya |
|---|---|
| IPK | Rata-rata nilai akademik calon |
| Tes Kemampuan | Hasil tes kemampuan calon |
| Kedisiplinan | Tingkat kedisiplinan calon |
| Kerja Sama | Kemampuan calon bekerja dalam tim |

Semua nilai dalam aplikasi ini memakai **skala 0 sampai 5** (0 = paling rendah, 5 = paling tinggi/sempurna).

### 3.2 Aspek — "Pengelompokan kriteria"

Aspek adalah **wadah/kelompok** untuk beberapa kriteria yang dianggap sejenis. Tujuannya agar nilai kecocokan bisa dilihat per kelompok, tidak hanya satu angka besar.

Contoh pengelompokan:

| Aspek | Isi Kriteria |
|---|---|
| **Intelektual** | IPK, Tes Kemampuan |
| **Sikap** | Kedisiplinan, Kerja Sama |

Setiap aspek juga punya **bobot aspek** — seberapa besar pengaruh kelompok tersebut terhadap nilai akhir (misalnya Intelektual 40%, Sikap 60%).

### 3.3 Profil Departemen — "Orang seperti apa yang dicari?"

Untuk setiap departemen, pengguna mengisi **profil yang diinginkan**. Satu baris profil terdiri dari:

- **Kriteria** yang dinilai (dipilih dari daftar kriteria),
- **Target** — nilai ideal calon untuk kriteria itu (0–5). Calon yang nilainya *tepat sama* dengan target dianggap sempurna,
- **Bobot** — atribut kriteria (0–1) yang **tidak lagi dipakai dalam hitungan**; hanya tersimpan sebagai data cadangan,
- **Tipe** — **Core (inti)** untuk kriteria yang wajib/sangat menentukan, atau **Secondary (pendukung)** untuk kriteria pelengkap,
- **Aspek** — kelompok tempat kriteria itu berada.

---

## 4. Inti Perhitungan (Langkah demi Langkah)

Bagian ini adalah **jantung algoritma**. Kita ikuti satu kandidat bernama **Budi** yang dinilai untuk departemen "Administrasi".

### Langkah 1 — Mencari selisih (gap)

Untuk setiap kriteria, hitung **selisih = nilai calon dikurangi target**.

Contoh profil departemen dan nilai Budi:

| Kriteria | Target | Nilai Budi | Selisih |
|---|---|---|---|
| IPK | 4 | 3 | 3 − 4 = **−1** |
| Tes Kemampuan | 4 | 3 | 3 − 4 = **−1** |
| Kedisiplinan | 4 | 4 | 4 − 4 = **0** |
| Kerja Sama | 4 | 3 | 3 − 4 = **−1** |

### Langkah 2 — Mengubah selisih menjadi skor kecocokan

Selisih belum bisa dipakai langsung. Peta berikut mengubah selisih menjadi **skor kecocokan** (semakin besar skor, semakin cocok):

| Selisih | Skor | Artinya |
|---|---|---|
| 0 | **5** | Tepat seperti yang dicari (paling sempurna) |
| +1 | **4,5** | Sedikit di atas target (masih bagus) |
| −1 | **4** | Sedikit di bawah target (cukup bagus) |
| +2 | **3,5** | Agak di atas target |
| −2 | **3** | Agak di bawah target |
| +3 | **2,5** | Jauh di atas target |
| −3 | **2** | Jauh di bawah target |
| +4 | **1,5** | Sangat di atas target |
| −4 | **1** | Sangat di bawah target |
| > +4 | **0,5** | Melebihi batas atas |
| < −4 | **0** | Melampaui batas bawah |

> Perhatikan: nilai yang **tepat sama dengan target** mendapat skor tertinggi (5). Nilai yang melebihi target pun tidak dianggap sempurna, karena inti metode ini adalah **kecocokan**, bukan sekadar tinggi-rendahnya nilai.

Skor Budi setelah konversi:

| Kriteria | Selisih | Skor |
|---|---|---|
| IPK | −1 | 4 |
| Tes Kemampuan | −1 | 4 |
| Kedisiplinan | 0 | 5 |
| Kerja Sama | −1 | 4 |

### Langkah 3 — Menghitung nilai per kelompok aspek

Kriteria dikelompokkan ke aspek. Di tiap aspek ada kriteria bertipe **inti** dan **pendukung**. Skor-skor tadi digabung per kelompok memakai **rata-rata biasa** (semua sub-kriteria diperlakukan setara, tanpa bobot kriteria):

- **Nilai Inti (NCF)** = rata-rata skor seluruh kriteria inti di dalam aspek.
- **Nilai Pendukung (NSF)** = rata-rata skor seluruh kriteria pendukung di dalam aspek.

Analoginya seperti menghitung nilai rapor tanpa penimbang: semua sub-kriteria dinilai sama, lalu hasilnya digabung.

Contoh: aspek **Intelektual** berisi IPK dan Tes Kemampuan, keduanya bertipe **inti**. Karena Budi mendapat skor 4 dan 4:

- Nilai Inti = (4 + 4) / 2 = **4,0**
- Nilai Pendukung = tidak ada kriteria pendukung di aspek ini → **0**

Contoh aspek **Sikap** berisi Kedisiplinan (tipe **inti**) dan Kerja Sama (tipe **pendukung**):

- Nilai Inti = 5 / 1 = **5,0**
- Nilai Pendukung = 4 / 1 = **4,0**

> Catatan: jika sebuah kriteria belum dinilai, kriteria itu dilewati (tidak ikut dihitung). Jika tidak ada kriteria pendukung sama sekali, Nilai Pendukung dianggap 0.

### Langkah 4 — Menggabungkan inti & pendukung menjadi Nilai Aspek

Nilai aspek dihitung dengan **porsi tetap dari aplikasi**: **60% untuk kriteria inti dan 40% untuk kriteria pendukung**.

- Nilai Aspek = (60% × Nilai Inti) + (40% × Nilai Pendukung)

Contoh untuk Budi:

| Aspek | Nilai Inti | Nilai Pendukung | Nilai Aspek |
|---|---|---|---|
| Intelektual | 4,0 | 0 | 0,6 × 4,0 + 0,4 × 0 = **2,4** |
| Sikap | 5,0 | 4,0 | 0,6 × 5,0 + 0,4 × 4,0 = **4,6** |

### Langkah 5 — Menggabungkan semua aspek menjadi Nilai Akhir

Setiap aspek punya **bobot aspek** (pengaruh terhadap hasil akhir). Nilai akhir dihitung dari **rata-rata berbobot nilai aspek**.

Misalnya bobot aspek: Intelektual = 40%, Sikap = 60%.

- Nilai Akhir Budi = (2,4 × 0,4 + 4,6 × 0,6) / (0,4 + 0,6) = (0,96 + 2,76) / 1,0 = **3,72**

> Nilai akhir (3,72) terlihat lebih kecil dari skor per kriteria karena sudah dirata-ratakan dengan bobot — ini wajar. Yang penting adalah **perbandingan antar calon**, bukan angka mutlaknya.

### Langkah 6 — Menentukan peringkat

Semua calon dihitung dengan cara yang sama untuk departemen yang sama, lalu **diurutkan dari nilai akhir terbesar ke terkecil**. Calon dengan nilai akhir paling besar berada di **peringkat pertama** (dianggap paling cocok).

---

## 5. Contoh Perbandingan Dua Calon (Agar Lebih Jelas)

Sekarang kita bandingkan Budi dengan calon lain, **Ani**, untuk departemen yang sama.

| Kriteria | Target | Nilai Budi | Skor Budi | Nilai Ani | Skor Ani |
|---|---|---|---|---|---|
| IPK | 4 | 3 | 4 | 4 | 5 |
| Tes Kemampuan | 4 | 3 | 4 | 4 | 5 |
| Kedisiplinan | 4 | 4 | 5 | 3 | 4 |
| Kerja Sama | 4 | 3 | 4 | 4 | 5 |

Perhitungan per aspek dan nilai akhir:

| Aspek | Bagian | Budi | Ani |
|---|---|---|---|
| Intelektual | Nilai Inti | 4,0 | 5,0 |
| Intelektual | Nilai Pendukung | 0 | 0 |
| Intelektual | **Nilai Aspek** | **2,4** | **3,0** |
| Sikap | Nilai Inti | 5,0 | 4,0 |
| Sikap | Nilai Pendukung | 4,0 | 5,0 |
| Sikap | **Nilai Aspek** | **4,6** | **4,4** |
| | **Nilai Akhir** | **(2,4×0,4 + 4,6×0,6) = 3,72** | **(3,0×0,4 + 4,4×0,6) = 3,84** |

Hasil peringkat:

| Peringkat | Nama | Nilai Akhir |
|---|---|---|
| **1** | **Ani** | **3,84** |
| 2 | Budi | 3,72 |

Menarik: Budi lebih disiplin, tetapi Ani lebih unggul di tiga kriteria lain, sehingga Ani menang tipis. Inilah inti SPK — **keputusan bukan ditentukan satu kriteria saja, melainkan gabungan seluruh kriteria dengan bobotnya masing-masing**.

---

## 6. Sifat "Cerdas" Aplikasi: Menyimpan Hasil Agar Cepat

Agar tidak menghitung ulang dari nol setiap kali laporan dibuka, aplikasi **menyimpan hasil peringkat** yang sudah pernah dihitung. Saat hasil itu dibutuhkan lagi, aplikasi tinggal menampilkannya — tanpa menghitung ulang. Ini membuat aplikasi terasa cepat, terutama jika calonnya banyak.

Namun aplikasi juga **waspada**: begitu ada data yang diubah — entah kriteria, target, bobot, aspek, calon, maupun nilainya — hasil simpanan yang lama **langsung dibuang** dan diganti dengan perhitungan baru saat diminta. Dengan kata lain: **hasil yang ditampilkan selalu segar dan sesuai data terbaru**.

---

## 7. Hal-Hal Penting yang Perlu Diingat

1. **Skala nilai selalu 0–5**, baik untuk target, nilai calon, maupun hasil akhir (hasil akhir umumnya berupa angka desimal seperti 3,72).
2. **Tepat di target = sempurna.** Nilai di atas target tidak otomatis lebih baik; yang dicari adalah **kecocokan**.
3. **Pembobotan tetap berpengaruh, tapi bukan di kriteria.** Bobot kriteria tidak lagi memengaruhi hasil, tetapi porsi **core (60%) vs secondary (40%)** dan **bobot aspek** sangat menentukan hasil akhir. Pastikan pengaturan tipe (core/secondary) dan bobot aspek sudah sesuai kebutuhan sebelum mengambil keputusan.
4. **Kriteria yang belum dinilai dilewati** — tidak ikut dihitung, tidak mengganggu hasil.
5. **Peringkat bersifat relatif per departemen**: peringkat 1 artinya calon paling cocok *di antara calon-calon yang dinilai untuk departemen itu*, bukan berarti nilainya mutlak sempurna.
6. **Hasil bisa diekspor** menjadi laporan (PDF) atau data (JSON) untuk arsip dan dokumentasi.

---

*Dokumen ini menjelaskan pola kerja perhitungan (algoritma) secara umum dan dengan contoh angka. Nilai/bobot asli pada aplikasi dapat berbeda, tetapi urutan langkah dan rumusnya tetap sama.*