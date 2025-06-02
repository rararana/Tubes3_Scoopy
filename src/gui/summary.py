import flet as ft

## masih hardcode

def create_summary_page(page: ft.Page):
    
    # Header
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
            "Wardes",
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
            ft.Text("Birthdate: 05-19-2025", size=12, color="#5A4935"),
            ft.Text("Address: Masjid Salman ITB", size=12, color="#5A4935"),
            ft.Text("Phone: 08293282838", size=12, color="#5A4935"),
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
    
    # Skills Section
    skills_section = ft.Column([
        ft.Container( 
            content=ft.Text(
                "Skills",
                size=16,
                weight=ft.FontWeight.BOLD,
                color="#5A4935",
            ),
            margin=ft.margin.only(left=50),
        ),
        ft.Row([
            ## masih hardcode
            ft.Container(
                content=ft.Text("React", color="white", size=12, weight=ft.FontWeight.BOLD),
                bgcolor="#7C3B00",
                margin=ft.margin.only(left=50),
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                border_radius=5
            ),
            ft.Container(
                content=ft.Text("React", color="white", size=12, weight=ft.FontWeight.BOLD),
                bgcolor="#7C3B00",
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                border_radius=5
            ),
            ft.Container(
                content=ft.Text("HTML", color="white", size=12, weight=ft.FontWeight.BOLD),
                bgcolor="#7C3B00",
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                border_radius=5
            ),
        ], spacing=10)
    ], spacing=10)
    
    # Job History Section
    job_history_box = ft.Container(
        width=500,
        height=200,
        bgcolor="#DFCAAD",
        border=ft.border.all(1, "#5A4935"),
        margin=ft.margin.only(left=50),
        content=ft.Stack([
            ft.Container(),  # Empty main content
            ft.Container(
                content=ft.Container(
                    width=40,
                    height=40,
                    bgcolor="#FF6347",
                    border_radius=20,
                    content=ft.Text("👤", color="white", text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center
                ),
                right=10,
                bottom=10
            )
        ])
    )
    
    job_history = ft.Column([
        ft.Container( 
            content=ft.Text(
                "Job History",
                size=16,
                weight=ft.FontWeight.BOLD,
                color="#5A4935",
            ),
            margin=ft.margin.only(left=50),
        ),
        job_history_box
    ], spacing=10)
    
    # Education Section
    education_box = ft.Container(
        width=250,
        height=150,
        bgcolor="#DFCAAD",
        border=ft.border.all(1, "#5A4935"),

    )
    
    education_section = ft.Column([
        ft.Text(
            "Education",
            size=16,
            weight=ft.FontWeight.BOLD,
            color="#5A4935"
        ),
        education_box
    ], spacing=5)
    
    # Interest Section
    interest_box = ft.Container(
        width=250,
        height=150,
        bgcolor="#DFCAAD",
        border=ft.border.all(1, "#5A4935"),

    )
    
    interest_section = ft.Column([
        ft.Text(
            "Interest",
            size=16,
            weight=ft.FontWeight.BOLD,
            color="#5A4935"
        ),
        interest_box
    ], spacing=5)
    
    # Left Column
    left_column = ft.Column([
        personal_info,
        ft.Container(height=8),
        skills_section,
        ft.Container(height=8),
        job_history
    ], spacing=0)
    
    # Right Column  
    right_column = ft.Column([
        ft.Container(height=8),  
        education_section,
        ft.Container(height=8),
        interest_section
    ], spacing=0)
    
    # Main layout
    main_row = ft.Row([
        ft.Container(left_column, expand=2),
        ft.Container(width=20), 
        ft.Container(right_column, expand=1)
    ])
    
    page_content = ft.Column([
        header,
        ft.Container(height=30),
        main_row
    ])
    
    main_container = ft.Container(
        content=page_content,
        bgcolor="#F6E7D0",
        expand=True
    )
    
    return main_container
