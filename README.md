# ScoopyHire CV Analyzer
**Advanced Applicant Tracking System with String Matching Algorithms**

---

## 📖 Deskripsi Singkat

ScoopyHire adalah aplikasi Applicant Tracking System (ATS) yang menggunakan algoritma string matching untuk mencari dan menganalisis CV kandidat. Aplikasi ini mengimplementasikan tiga algoritma pencarian: **KMP (Knuth-Morris-Pratt)**, **Boyer-Moore**, dan **Aho-Corasick** dengan dukungan fuzzy matching untuk memberikan hasil pencarian yang optimal.

---

## 🔍 Algoritma yang Diimplementasikan

### **1. KMP (Knuth-Morris-Pratt)**
- **Kompleksitas**: O(n + m) dimana n = panjang teks, m = panjang pattern
- **Cara Kerja**: Menggunakan preprocessing untuk membuat tabel LPS (Longest Proper Prefix which is also Suffix) yang memungkinkan algoritma untuk menghindari backtracking pada teks
- **Keunggulan**: Tidak pernah mundur pada teks, efisien untuk pencarian single pattern
- **Implementasi**: Optimal untuk pencarian kata kunci tunggal dengan performa konsisten

### **2. Boyer-Moore**
- **Kompleksitas**: O(n × m) worst case, O(n/m) best case
- **Cara Kerja**: Menggunakan bad character heuristic, memindai pattern dari kanan ke kiri dan dapat melompati karakter yang tidak cocok
- **Keunggulan**: Sangat efisien untuk pattern panjang, dapat skip multiple karakter sekaligus
- **Implementasi**: Excellent performance untuk keyword yang panjang dan unique

### **3. Aho-Corasick**
- **Kompleksitas**: O(n + m + z) dimana z = jumlah kemunculan pattern
- **Cara Kerja**: Membangun automaton finite state untuk mencari multiple pattern secara simultan dalam satu pass
- **Keunggulan**: Optimal untuk pencarian multiple keywords sekaligus
- **Implementasi**: Superior untuk pencarian dengan banyak kata kunci

---

## ⚙️ Requirements & Instalasi

### **System Requirements**
- **Python**: 3.8 atau lebih tinggi
- **MySQL**: 5.7 atau lebih tinggi
- **RAM**: Minimum 4GB
- **Storage**: 2GB free space

### **Dependencies Installation**

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server

# 2. Install PDF viewers (optional untuk View CV)
sudo apt install evince okular chromium-browser

# 3. Setup MySQL (ikuti instruksi setup)
sudo mysql_secure_installation
```

### **Python Environment Setup**

```bash
# 1. Clone repository
git clone https://github.com/rararana/Tubes3_Scoopy.git
cd Tubes3_Scoopy

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install pymupdf PyQt5 flet mysql-connector-python faker
```

### **Database Setup**

```bash
# 1. Login ke MySQL sebagai root
sudo mysql -u root -p

# 2. Create database dan user
CREATE DATABASE cv_ats;
CREATE USER 'ats_user'@'localhost' IDENTIFIED BY 'Ats_Pass11';
GRANT ALL PRIVILEGES ON tubes3_seeding.* TO 'ats_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 3. Import database schema dan data
mysql -u ats_user -p tubes3_seeding < src/database/tubes3_seeding.sql
```

---

## 🚀 Cara Menjalankan Program

### **1. Ekstraksi Data CV (First Time Setup)**
```bash
# Activate virtual environment
source venv/bin/activate

# Extract PDF files to text for pattern matching
python src/database/extract_and_store.py
```

### **2. Menjalankan Aplikasi GUI**
```bash
# Activate virtual environment
source venv/bin/activate

# Run main application
python3 src/main.py
```

---

## 📱 Cara Penggunaan

### **GUI Application Flow:**

1. **Landing Page**: Klik tombol "Get Started"
2. **Search Page**: 
   - Masukkan keywords (comma-separated)
   - Pilih algoritma (KMP/BM/AC)
   - Set jumlah hasil maksimal
   - Klik "Search CV"
3. **Results Page**: 
   - Lihat hasil dengan match statistics
   - Klik "View Details" untuk summary CV
   - Klik "View CV" untuk buka PDF
4. **Summary Page**: 
   - Lihat informasi lengkap kandidat
   - Klik "Back to Search" untuk kembali

### **Features:**
- ✅ **Real-time Search** dengan 3 algoritma berbeda
- ✅ **Fuzzy Matching** untuk toleransi typo
- ✅ **Performance Metrics** dalam milliseconds
- ✅ **PDF Integration** dengan system viewer
- ✅ **Database Integration** dengan MySQL
- ✅ **Responsive UI** dengan Flet framework

---

## 🗂️ Struktur Database

### **ApplicantProfile Table**
```sql
- applicant_id (Primary Key)
- first_name, last_name  
- date_of_birth
- address, phone_number
```

### **ApplicationDetail Table**
```sql
- application_id (Primary Key)
- applicant_id (Foreign Key)
- application_role
- cv_path
```

### **Data Statistics:**
- **480 Real CVs** dalam 24 kategori pekerjaan
- **100 Profil Pelamar** dengan data personal
- **Support Multiple File Formats** (PDF, TXT, JSON)

---

## 🛠️ Troubleshooting

### **Database Issues**
```bash
# Check database connection
mysql -u ats_user -p cv_ats -e "SELECT COUNT(*) FROM ApplicantProfile;"

# Re-import if needed
mysql -u ats_user -p cv_ats < src/database/init_db.sql
```

### **Missing PDF Viewer**
```bash
# Install additional viewers
sudo apt install evince okular firefox-esr
```

### **Python Dependencies**
```bash
# Reinstall if needed
pip install --upgrade -r requirements.txt
```

---

## 👥 Author

Dikembangkan oleh **Kelompok 31 - Scoopy**:

| Nama | NIM |
|------|-----|
| **Wardatul Khoiroh** | 13523001 |
| **Ranashahira Reztaputri** | 13523007 |
| **Diyah Susan Nugrahani** | 13523080 |

---


## 📝 License

Project ini dibuat untuk keperluan tugas besar **IF2211 Strategi Algoritma** ITB 2024.

---

**© 2024 ScoopyHire Team - Institut Teknologi Bandung
