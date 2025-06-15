# Database configurations dengan fallback
PRIMARY_DB_CONFIG = {
    "host": "localhost",
    "user": "ats_user",
    "password": "Ats_Pass11",
    "database": "tubes3_seeding"  # Primary database
}

FALLBACK_DB_CONFIG = {
    "host": "localhost",
    "user": "ats_user", 
    "password": "Ats_Pass11",
    "database": "cv_ats"  # Fallback database
}

# Default configuration (akan digunakan jika tidak ada error)
DB_CONFIG = PRIMARY_DB_CONFIG