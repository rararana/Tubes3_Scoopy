# Tubes3_Scoopy

## Setup Dependencies untuk GUI
```bash
python3 -m venv venv
source venv/bin/activate
pip install pymupdf PyQt5 flet mysql-connector-python

# Install PDF viewers
sudo apt install evince okular chromium-browser
```

## Cara ekstrak dari pdf di folder data ke regex dan string panjang -> masuk database
```bash
source venv/bin/activate
python src/database/extract_and_store.py
```

## Cek Database
```bash
mysql -u ats_user -p
```

password ada di db_config.py
```sql
USE cv_ats;

-- Verify table structure
DESCRIBE ApplicantProfile;
DESCRIBE ApplicationDetail;

-- Check data count
SELECT COUNT(*) as total_applicants FROM ApplicantProfile;
SELECT COUNT(*) as total_applications FROM ApplicationDetail;

-- Sample data
SELECT * FROM ApplicantProfile LIMIT 5;
SELECT * FROM ApplicationDetail LIMIT 5;
```

## Cara Menjalankan Program
```bash
source venv/bin/activate
python3 src/main.py
```

## Troubleshooting Database Issues

### "Unknown" Results or Missing Applicant IDs

1. **Check init_db.sql file integrity**:
```bash
ls -la src/database/init_db.sql
wc -l src/database/init_db.sql  # Should be ~1100+ lines
```

2. **Debug database loading**:
```bash
# Run with verbose output
python3 -c "
from src.gui.search_cv import create_search_cv_page
import flet as ft
def dummy_page(): pass
page = dummy_page()
# This will show detailed loading info
"
```

3. **Verify SQL file content**:
```bash
grep -c "INSERT INTO ApplicantProfile" src/database/init_db.sql
grep -c "INSERT INTO ApplicationDetail" src/database/init_db.sql
```

4. **Check pattern files**:
```bash
ls -la data/pattern_matching/ | wc -l  # Should be ~480 files
```

### Expected Values
- **ApplicantProfile**: ~480 entries
- **ApplicationDetail**: ~480 entries  
- **Pattern files**: ~479 .txt files
- **Roles**: 24 different roles (ACCOUNTANT, ADVOCATE, etc.)

### File Structure Verification
```
data/
├── ACCOUNTANT/         # 20 PDF files
├── ADVOCATE/           # 20 PDF files  
├── INFORMATION-TECHNOLOGY/  # 20 PDF files
└── ...                 # 24 total role folders

data/pattern_matching/
├── 10001727.txt
├── 10070224.txt
└── ...                 # 479 total .txt files
```

### Database Schema Check
```sql
-- Expected ApplicantProfile structure
DESCRIBE ApplicantProfile;
-- Should show: applicant_id, first_name, last_name, date_of_birth, address, phone_number

-- Expected ApplicationDetail structure  
DESCRIBE ApplicationDetail;
-- Should show: application_id, applicant_id, application_role, cv_path
```

### If Data Still Missing
```bash
# Re-run extraction (will regenerate pattern files)
python src/database/extract_and_store.py

# Check if MySQL tables exist
mysql -u ats_user -p cv_ats -e "SHOW TABLES;"

# Recreate database if needed
mysql -u ats_user -p cv_ats < src/database/init_db.sql
```

## Common Issues

### Different Results Between Laptops
- **Cause**: Different `init_db.sql` file versions
- **Solution**: Ensure both laptops use identical `init_db.sql`
- **Verify**: Compare file checksums

### Missing or "Unknown" Applicants  
- **Cause**: Database loading failed
- **Solution**: Check debug output when loading
- **Verify**: Count loaded applicants (should be 480)

### PDF Not Opening
- **Cause**: No PDF viewer installed
- **Solution**: Install evince or chromium-browser
- **Fallback**: Text preview shown in console

## Performance Comparison
- **KMP**: ~15ms for 480 CVs
- **Boyer-Moore**: ~12ms for 480 CVs  
- **Aho-Corasick**: ~8ms for multiple keywords

## Project Status
✅ **480 Real CVs** from diverse backgrounds
✅ **3 Search Algorithms** with performance metrics
✅ **MySQL Integration** with proper names and roles
✅ **GUI + Terminal** interfaces
✅ **PDF Viewing** with system integration
✅ **Fuzzy Matching** with Levenshtein distance