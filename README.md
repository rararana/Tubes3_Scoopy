# Tubes3_Scoopy

## Cara ekstrak dari pdf di folder data ke regex dan string panjang -> masuk database
```
python3 -m venv venv
source venv/bin/activate
pip install pymupdf

python src/database/extract_and_store.py
```

## Cek Database
```
mysql -u ats_user -p
```

password ada di db_config.py
```
USE cv_ats;
SELECT * FROM ApplicantProfile;
SELECT * FROM ApplicationDetail;
```

## Cara Menjalankan Program
```
python3 src/search_kmp_terminal.py
```
