import os
import json
import mysql.connector
from ..database.db_connector import connect 
from .boyer_moore import boyer_moore_search 

STRUCTURED_INFO_DIR = "data/structured_info/"

def get_applicant_structured_data():
    applicant_data = []
    conn = None
    cursor = None
    try:
        conn = connect()
        cursor = conn.cursor(dictionary=True) 

        # query untuk mendapatkan metadata pelamar dan path CV dari database
        query = """
            SELECT ap.first_name, ap.last_name, ap.phone_number, ad.cv_path
            FROM ApplicantProfile ap
            JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id;
        """
        cursor.execute(query)
        db_results = cursor.fetchall()

        if not db_results:
            print("Tidak ada metadata pelamar yang ditemukan di database.")
            return []

        for row in db_results:
            cv_path = row['cv_path']
            # ekstrak nama file dari cv_path 
            filename_without_ext = os.path.splitext(os.path.basename(cv_path))[0]
            json_filepath = os.path.join(STRUCTURED_INFO_DIR, f"{filename_without_ext}.json")

            if os.path.exists(json_filepath):
                try:
                    with open(json_filepath, 'r', encoding='utf-8') as f:
                        structured_info = json.load(f)
                        # Gabungkan metadata dari DB dengan info terstruktur dari JSON
                        applicant_full_info = {
                            "first_name": row['first_name'],
                            "last_name": row['last_name'],
                            "phone": row['phone_number'],
                            "summary": structured_info.get("summary", ""),
                            "highlights": structured_info.get("highlights", ""),
                            "accomplishments": structured_info.get("accomplishments", ""),
                            "experience": structured_info.get("experience", ""),
                            "education": structured_info.get("education", ""),
                            "skills": structured_info.get("skills", "")
                        }
                        applicant_data.append(applicant_full_info)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON dari {json_filepath}: {e}")
                except Exception as e:
                    print(f"Error membaca file {json_filepath}: {e}")
            else:
                print(f"Peringatan: File JSON info terstruktur tidak ditemukan untuk {cv_path} di {json_filepath}. Melewati.")

    except mysql.connector.Error as err:
        print(f"Error database: {err}")
    except Exception as e:
        print(f"Terjadi error tak terduga: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return applicant_data

def search_applicants_by_keyword(keyword):
    """
    mencari pelamar yang memiliki kata kunci tertentu di bidang-bidang relevan.
    """
    found_applicants = []
    # mengambil data terstruktur dari database dan file JSON
    all_applicants = get_applicant_structured_data()
    
    if not all_applicants:
        print("Tidak ada data pelamar yang ditemukan untuk dicari.")
        return []

    print(f"\nMencari kata kunci: '{keyword}'...")
    
    normalized_keyword = keyword.lower()

    for applicant in all_applicants:
        applicant_full_text = ""
        # structured_info yang dimuat dari JSON
        if "summary" in applicant:
            applicant_full_text += applicant["summary"] + " "
        if "skills" in applicant:
            applicant_full_text += applicant["skills"] + " "
        if "experience" in applicant:
            applicant_full_text += applicant["experience"] + " "
        if "education" in applicant:
            applicant_full_text += applicant["education"] + " "
        if "highlights" in applicant:
            applicant_full_text += applicant["highlights"] + " "
        if "accomplishments" in applicant:
            applicant_full_text += applicant["accomplishments"] + " "

        # normalisasi teks pelamar (huruf kecil)
        normalized_applicant_text = " ".join(applicant_full_text.lower().split())

        # algoritma Boyer-Moore
        matches = boyer_moore_search(normalized_applicant_text, normalized_keyword)

        if matches:
            found_applicants.append({
                "first_name": applicant.get("first_name", "N/A"),
                "last_name": applicant.get("last_name", "N/A"),
                "phone": applicant.get("phone", "N/A"),
                "matches_count": len(matches),
                "match_indices": matches 
            })
    return found_applicants

def main():
    # pastikan sudah menjalankan batch_process.py atau process_file.py
    # untuk mengisi direktori data/structured_info/ dan database Anda.

    # contoh penggunaan
    search_term1 = "assets"
    results1 = search_applicants_by_keyword(search_term1)
    if results1:
        print(f"\nPelamar yang cocok dengan '{search_term1}':")
        for res in results1:
            print(f"- {res['first_name']} {res['last_name']} (Telepon: {res['phone']}), Cocok: {res['matches_count']}")
    else:
        print(f"\nTidak ada pelamar yang cocok dengan '{search_term1}'.")

main()