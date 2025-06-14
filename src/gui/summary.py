import flet as ft
import re
import os

from services.database_service import load_applicant_by_exact_filename_from_db
from services.file_service import parse_cv_text_file

def create_summary_page(result: dict, on_back_click=None):
    """
    Membuat halaman ringkasan CV.
    """
    path_without_extension = os.path.splitext(result["filename"])[0]

    profile_data = load_applicant_by_exact_filename_from_db(path_without_extension)
    cv_content = parse_cv_text_file(result["filename"])

    full_name = profile_data.get("full_name", "Unknown Applicant")
    date_of_birth = profile_data.get("date_of_birth", "N/A")
    address = profile_data.get("address", "N/A")
    phone_number = profile_data.get("phone_number", "N/A")

    skills_text = cv_content.get("Skills", "No skills listed.")
    experience_text = cv_content.get("Experience", "No experience listed.")
    education_text = cv_content.get("Education", "No education details available.")
    
    header = ft.Column([
        ft.Container(height=8, bgcolor="#4A2C17", width=float("inf")),
        ft.Container(
            content=ft.Column([
                ft.Text("CV Summary", size=48, color="#5D2E0A", weight=ft.FontWeight.BOLD),
                ft.Container(height=2, bgcolor="#5D2E0A", width=300, margin=ft.margin.symmetric(vertical=5)),
                ft.Row([ft.Text(c, size=14, color="#5D2E0A") for c in "SCOOPY HIRE"], alignment=ft.MainAxisAlignment.CENTER, spacing=3)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            margin=ft.margin.only(top=30, bottom=40),
        ),
    ])

    personal_info_card = ft.Column([
        ft.Container(
            content=ft.Text(full_name, size=14, weight=ft.FontWeight.BOLD, color="white"),
            bgcolor="#5A4935", padding=8
        ),
        ft.Container(
            content=ft.Column([
                ft.Text(f"Birthdate: {date_of_birth}", size=12, color="#5A4935", weight=ft.FontWeight.BOLD),
                ft.Text(f"Address: {address}", size=12, color="#5A4935", weight=ft.FontWeight.BOLD),
                ft.Text(f"Phone: {phone_number}", size=12, color="#5A4935", weight=ft.FontWeight.BOLD),
            ], spacing=5),
            bgcolor="#DFCAAD", padding=8, border=ft.border.all(1, "#5A4935")
        )
    ], spacing=0)

    skills_list = re.split(r'[,;\n]+', skills_text)
    skill_pills = [
        ft.Container(
            content=ft.Text(skill.strip(), color="white", size=12, weight=ft.FontWeight.W_500),
            bgcolor="#8B4513", padding=ft.padding.symmetric(horizontal=15, vertical=8), border_radius=5
        ) for skill in skills_list if skill.strip()
    ][:4]
    
    skills_section = ft.Column([
        ft.Text("Skills", size=20, weight=ft.FontWeight.BOLD, color="#5A4935"),
        ft.Row(controls=skill_pills, spacing=10)
    ], spacing=10)

    def create_info_box(title, text_content, height):
        return ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color="#5A4935"),
            ft.Container(
                content=ft.Column(
                    [ft.Text(text_content, size=12, color="#5A4935", weight=ft.FontWeight.BOLD)],
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=15, border=ft.border.all(1, "#5A4935"), bgcolor="#DFCAAD", height=height
            )
        ], spacing=10)

    job_section = create_info_box("Job history", experience_text, height=200)
    education_section = create_info_box("Education", education_text, height=430)
    
    left_column = ft.Column([
        personal_info_card, ft.Container(height=30),
        skills_section, ft.Container(height=30),
        job_section
    ], spacing=0, expand=2)

    right_column = ft.Column([education_section], spacing=0, expand=1)
    
    back_button = ft.ElevatedButton(
        "Back to Search", icon=ft.Icons.ARROW_BACK,
        on_click=lambda e: on_back_click(e) if on_back_click else None,
        style=ft.ButtonStyle(bgcolor="#5A4935", color="white")
    )
    
    main_container = ft.Container(
        content=ft.Column([
            header,
            ft.Container(
                content=ft.Row([left_column, right_column], spacing=40, vertical_alignment=ft.CrossAxisAlignment.START),
                padding=ft.padding.symmetric(horizontal=50)
            ),
            ft.Container(
                content=ft.Row([back_button], alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.only(right=50, bottom=20, top=20)
            )
        ], scroll=ft.ScrollMode.AUTO),
        bgcolor="#F6E7D0", expand=True
    )
    
    return main_container