# Tubes3_Scoopy

Aplikasi ini membaca file PDF dari folder `data/`, mengekstrak teks menggunakan `pymupdf`, mencocokkan informasi penting dengan regex, dan menyimpannya ke dalam database MySQL. Antarmuka dibangun dengan [Flet](https://flet.dev/) (berbasis Flutter) dan menggunakan `mpv` untuk pemutar media jika dibutuhkan.

---

## ✅ Persiapan Awal

### 1. Buat Virtual Environment dan Install Dependensi
```bash
python3 -m venv venv
source venv/bin/activate
pip install pymupdf PyQt5 flet
```

### 2. Install `mpv` dan pustaka `libmpv`
```bash
sudo apt update
sudo apt install mpv libmpv2 libmpv-dev
```

> **Catatan:**  
> Jika setelah instalasi muncul error seperti berikut saat menjalankan program:
> 
> ```
> error while loading shared libraries: libmpv.so.1: cannot open shared object file
> ```
> 
> Maka jalankan:
> 
> ```bash
> export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
> ```
> 
> Atau buat permanen di `~/.bashrc`:
> 
> ```bash
> echo 'export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH' >> ~/.bashrc
> source ~/.bashrc
> ```

---

## 📄 Ekstrak PDF dan Simpan ke Database

Jalankan script berikut untuk mengambil data dari PDF di folder `data/` dan menyimpannya ke database:

```bash
python src/database/extract_and_store.py
```

---

## 🛢️ Cek Isi Database

```bash
mysql -u ats_user -p
```

Password dapat ditemukan di file `src/database/db_config.py`.  
Setelah masuk ke MySQL, jalankan:

```sql
USE cv_ats;
SELECT * FROM ApplicantProfile;
SELECT * FROM ApplicationDetail;
```

---

## ▶️ Menjalankan Aplikasi

Aktifkan virtual environment jika belum:
```bash
source venv/bin/activate
```

Lalu jalankan aplikasi:
```bash
python3 src/main.py
```

---

## 🧩 Dependensi Utama

- Python 3.12+
- [pymupdf](https://pymupdf.readthedocs.io/)
- PyQt5
- [flet](https://flet.dev/)
- mpv, libmpv2, libmpv-dev
- MySQL Server

---

## 📬 Kontak

Silakan hubungi pengembang jika mengalami masalah lebih lanjut terkait dependensi atau lingkungan sistem.
