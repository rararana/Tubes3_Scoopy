import mysql.connector
from db_config import db_config

def connect():
    return mysql.connector.connect(**db_config)

def insert_applicant(first_name, last_name, dob, address, phone):
    conn = connect()
    cursor = conn.cursor()
    query = """
        INSERT INTO ApplicantProfile 
        (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (first_name, last_name, dob, address, phone))
    conn.commit()
    applicant_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return applicant_id

def insert_application_detail(applicant_id, role, cv_path):
    conn = connect()
    cursor = conn.cursor()
    query = """
        INSERT INTO ApplicationDetail 
        (applicant_id, application_role, cv_path)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (applicant_id, role, cv_path))
    conn.commit()
    cursor.close()
    conn.close()
