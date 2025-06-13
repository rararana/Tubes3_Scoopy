import flet as ft
import json
import re
import os
import mysql.connector # perlu install

def load_applicant_by_exact_filename_from_db(file_number):
   
    applicant_data = {} 

    DB_CONFIG = {
        "host": "localhost",
        "user": "ats_user",
        "password": "Ats_Pass11",
        "database": "cv_ats"
    }

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("Successfully connected to MySQL database!")
        
        cursor = conn.cursor(dictionary=True) 

        query = """
        SELECT
            ap.applicant_id,
            ap.first_name,
            ap.last_name,
            ap.date_of_birth,
            ap.address,
            ap.phone_number,
            ad.application_role,
            ad.cv_path
        FROM
            ApplicantProfile ap
        JOIN
            ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
        WHERE
            REPLACE(SUBSTRING_INDEX(ad.cv_path, '/', -1), '.pdf', '') = %s
        LIMIT 1;
        """

        cursor.execute(query, (file_number,))
        
        result = cursor.fetchone() 

        if result:
            print(f"Found applicant data for CV filename: '{file_number}'")
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
        else:
            print(f"No applicant found with CV file matching '{file_number}' in the database.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")
    
    return applicant_data


def parse_cv_text_file(filename: str) -> dict:
    parsed_data = {
        "Experience": "",
        "Education": "",
        "Skills": ""
    }

    filename = "data/regex_data/" + filename

    if not os.path.exists(filename):
        print(f"Error: CV text file not found at {filename}")
        return parsed_data

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        section_split_pattern = r'\n(?=^[A-Z]+[\w\s&/,-]*:?\s*$)'

        sections = re.split(section_split_pattern, content, flags=re.MULTILINE)

        current_section_key = None
        temp_content_buffer = []

        for section in sections:
            section = section.strip()
            if not section:
                continue

            lines = section.split('\n')
            if not lines:
                continue

            header = lines[0].strip()
            content_lines = lines[1:] if len(lines) > 1 else []
            section_content = '\n'.join(content_lines).strip()

            header_lower = header.lower().replace(':', '').strip()
            matched_key = None 

            if re.search(r'\b(experience|work\s+experience|employment|professional\s+experience|career|work\s+history|job\s+history)\b', header_lower):
                matched_key = "Experience"
            elif re.search(r'\b(education|training|qualifications?|academic|certifications?|degrees?|schooling|university|college)\b', header_lower):
                matched_key = "Education"
            elif re.search(r'\b(skills?|technical\s+skills?|core\s+competencies|expertise|competencies|abilities|proficiencies)\b', header_lower):
                matched_key = "Skills"
      
            if matched_key and temp_content_buffer:
                if current_section_key:
                    
                    parsed_data[current_section_key] += '\n' + '\n'.join(temp_content_buffer).strip()
               
                temp_content_buffer = [] 

            if matched_key:
                if matched_key == "Experience" and parsed_data["Experience"]:
                    parsed_data[matched_key] += "\n\n" + section_content
                else:
                    parsed_data[matched_key] = section_content
                current_section_key = matched_key 
            else:
              
                if current_section_key:
                    parsed_data[current_section_key] += '\n' + header
                    if section_content:
                        parsed_data[current_section_key] += '\n' + section_content
                else:
  
                    temp_content_buffer.append(header)
                    if section_content:
                        temp_content_buffer.append(section_content)

        if temp_content_buffer and current_section_key:
            parsed_data[current_section_key] += '\n' + '\n'.join(temp_content_buffer).strip()


    except Exception as e:
        print(f"An error occurred while parsing CV text file {filename}: {e}")

    print("Parsed CV Data:", parsed_data)
    return parsed_data


def create_summary_page(result, on_back_click=None):
    path = result["filename"]
    path_without_extension = os.path.splitext(path)[0]
    profile_data = load_applicant_by_exact_filename_from_db(path_without_extension)

    first_name = profile_data.get("first_name", "N/A") if profile_data else "N/A"
    last_name = profile_data.get("last_name", "") if profile_data else ""
    full_name = f"{first_name} {last_name}".strip() if first_name != "N/A" else result.get("name", "Unknown Applicant").split(' (')[0]

    date_of_birth = profile_data.get("date_of_birth", "N/A") if profile_data else "N/A"
    address = profile_data.get("address", "N/A") if profile_data else "N/A"
    phone_number = profile_data.get("phone_number", "N/A") if profile_data else "N/A"

    # data cv
    data = parse_cv_text_file(result["filename"])
    skills_text_raw = data.get("Skills", "No skills listed.")
    experience_text = data.get("Experience", "No experience listed.")
    education_text = data.get("Education", "No education details available.")

    # Back button
    back_button = ft.ElevatedButton(
        "Back to Search",
        icon=ft.Icons.ARROW_BACK,
        on_click=lambda e: on_back_click(e) if on_back_click else e.page.go("/"),
        style=ft.ButtonStyle(
            bgcolor="#5A4935",
            color="white",
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        ),
    )
    
    header = ft.Column([
        # Garis coklat tua di bagian atas
        ft.Container(
            height=8,
            bgcolor="#4A2C17",
            width=float("inf"),
        ),
        
        # Header dengan nama aplikasi
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "CV SUMMARY",
                        size=48,
                        color="#5D2E0A",
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        height=2,
                        bgcolor="#5D2E0A",
                        width=300,
                        margin=ft.margin.symmetric(vertical=10),
                    ),
                    ft.Text(
                        "SCOOPY HIRE",
                        size=14,
                        color="#5D2E0A",
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_400,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            margin=ft.margin.only(top=10, bottom=5),
        ),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
    
    # Personal Information Card 
    personal_info_header = ft.Container(
        content=ft.Text(
            full_name, #hard code
            size=12,
            weight=ft.FontWeight.BOLD,
            color="white"
        ),
        width=500,
        bgcolor="#5A4935",
        padding=5,
        margin=ft.margin.only(left=50),
        alignment=ft.alignment.center_left
    )
    
    personal_info_content = ft.Container(
        content=ft.Column([
            ft.Text(f"Birthdate: {date_of_birth}", size=12, color="#5A4935"),
            ft.Text(f"Address: {address}", size=12, color="#5A4935"),
            ft.Text(f"Phone: {phone_number}", size=12, color="#5A4935"),
        ]),
        width=500,
        bgcolor="#d2b48c",
        padding=5,
        margin=ft.margin.only(left=50),
        alignment=ft.alignment.center_left
    )
    
    personal_info = ft.Column([
        personal_info_header,
        personal_info_content
    ], spacing=0)
    
    #skills section
    skills_list = [skill.strip() for skill in re.split(r"[,\;\s]+", skills_text_raw) if skill.strip()]
    skills = skills_list[:4]
    if isinstance(skills, str):
        skills = [skills]  

    skill_containers = [
        ft.Container(
            content=ft.Text(skill, color="white", size=12, weight=ft.FontWeight.BOLD),
            bgcolor="#7C3B00",
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            border_radius=5,
            margin=ft.margin.only(left=50 if index == 0 else 0, right=10, bottom=5),
        )
        for index, skill in enumerate(skills)
    ]

    # Buat row untuk kontainer
    skills_row = ft.Row(skill_containers, spacing=10)
    skill_section = ft.Column(
        controls=[
            ft.Container(
                ft.Text(
                    "Skills",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#5A4935"
                ),
                margin=ft.margin.only(left=50),
            ),
            skills_row
        ],
        spacing=5,
    )

    jobs = [skill.strip() for skill in experience_text.split(";" or ",")]

    job_entries = [
        ft.Text(
            job,
            size=12,
            color="#5A4935",
            weight=ft.FontWeight.NORMAL
        )
        for job in jobs
    ]
    
    # job section
    job_box = ft.Container(
        content=ft.Column(
            job_entries,
            spacing=5,
            scroll=ft.ScrollMode.ADAPTIVE 
        ),
        width=600,
        height=400,
        bgcolor="#DFCAAD",
        padding=10,
        border=ft.border.all(1, "#5A4935"),
        border_radius=0,
        margin=ft.margin.only(left=50),  
    )
    
    job_section = ft.Column(
        controls=[
            ft.Container(
                ft.Text(
                    "Work History",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#5A4935"
                ),
                margin=ft.margin.only(left=50),
            ),
            job_box
        ],
        spacing=5,
    )

    educations = [skill.strip() for skill in education_text.split(";" or "," or "\n")]

    education_entries = [
        ft.Text(
            education,
            size=12,
            color="#5A4935",
            weight=ft.FontWeight.NORMAL
        )
        for education in educations
    ]
    
    # Education section
    education_box = ft.Container(
        content=ft.Column(
            education_entries,
            spacing=5,
            scroll=ft.ScrollMode.ADAPTIVE 
        ),
        width=400,
        height=300,
        bgcolor="#DFCAAD",
        padding=10,
        border=ft.border.all(1, "#5A4935"),
        border_radius=0,  
        margin=ft.margin.only(left=50)
    )
    
    education_section = ft.Column(
        controls=[
            ft.Container(
                ft.Text(
                    "Education",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#5A4935"
                ),
                margin=ft.margin.only(left=50)
            ),
            education_box
        ],
        spacing=5
    )
    
    # Left Column
    left_column = ft.Column([
        personal_info,
        ft.Container(height=8),
        skill_section,
        ft.Container(height=8),
        education_section
        
    ], spacing=0)
    
    # Right Column  
    right_column = ft.Column([
        ft.Container(height=8), 
        job_section, 
        ft.Container(height=8),
    ], spacing=0)
    
    # main layout
    main_row = ft.Row([
        ft.Container(left_column, expand=1.5),
        ft.Container(width=10), 
        ft.Container(right_column, expand=1)
    ])
    
    # back button
    footer = ft.Container(
        content=ft.Row(
            [back_button],
            alignment=ft.MainAxisAlignment.END,
        ),
        padding=ft.padding.only(right=20, bottom=20),
    )
    
    page_content = ft.Column(
        [
            header,
            ft.Container(height=30),
            main_row,
            footer
        ],
        scroll=ft.ScrollMode.AUTO,  # Tambahkan scroll di sini
    )
    
    main_container = ft.Container(
        content=page_content,
        bgcolor="#F6E7D0",
        expand=True
    )
    
    return main_container