import mysql.connector

DB_CONFIG = { "host": "localhost", "user": "ats_user", "password": "Ats_Pass11", "database": "cv_ats"}

def get_applicant_name_by_cv(filename: str) -> tuple[str, str]:
    """
    Mengambil nama pelamar dan peran dari database berdasarkan nama file CV.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        clean_filename = filename.replace(".txt", "")
        query = """
        SELECT ap.first_name, ap.last_name, ad.application_role
        FROM ApplicantProfile ap JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
        WHERE REPLACE(SUBSTRING_INDEX(ad.cv_path, '/', -1), '.pdf', '') = %s LIMIT 1;
        """
        cursor.execute(query, (clean_filename,))
        result = cursor.fetchone()
        
        if result:
            return f"{result['first_name']} {result['last_name']}", result['application_role']
        return f"Unknown: {filename}", "N/A"
    except Exception as e:
        print(f"DB Error in get_applicant_name_by_cv: {e}")
        return f"Unknown: {filename}", "N/A"
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def load_applicant_by_exact_filename_from_db(file_number: str) -> dict:
    """
    Mengambil detail lengkap data pelamar dari DB berdasarkan nama file (tanpa ekstensi).
    """
    applicant_data = {}
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT
            ap.applicant_id, ap.first_name, ap.last_name, ap.date_of_birth,
            ap.address, ap.phone_number, ad.application_role, ad.cv_path
        FROM ApplicantProfile ap
        JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
        WHERE REPLACE(SUBSTRING_INDEX(ad.cv_path, '/', -1), '.pdf', '') = %s
        LIMIT 1;
        """
        cursor.execute(query, (file_number,))
        result = cursor.fetchone()
        if result:
            applicant_data = {
                'applicant_id': result['applicant_id'],
                'first_name': result['first_name'],
                'last_name': result['last_name'],
                'full_name': f"{result['first_name']} {result['last_name']}",
                'date_of_birth': str(result['date_of_birth']),
                'address': result['address'],
                'phone_number': result['phone_number'],
                'role': result['application_role'],
                'cv_path': result['cv_path'],
                'cv_filename': file_number
            }
    except Exception as e:
        print(f"Database/Unexpected error in load_applicant: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return applicant_data