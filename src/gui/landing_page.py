import flet as ft
from .search_cv import create_search_cv_page

def create_landing_page(page: ft.Page):
    
    welcome_container = ft.Container(
        bgcolor="#F6E7D0", 
        expand=True,
        content=ft.Column(
            [
                ft.Container(
                    height=10,
                    bgcolor="#4A2C17",
                    width=float("inf"),
                ),

                ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Welcome to",
                                        size=26,
                                        color="#8B4513",
                                        weight=ft.FontWeight.NORMAL,
                                        font_family="Newsreader",
                                    ),
                                    ft.Text(
                                        "ScoopyHire",
                                        size=80,
                                        color="#5D2E0A",
                                        weight=ft.FontWeight.W_600,
                                        font_family="Newsreader",
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            margin=ft.margin.only(top=120, bottom=60),
                        ),
                        
                        ft.Container(
                            content=ft.Text(
                                "Stop guessing. Start matching. ScoopyHire gets the CVs\nyou need.",
                                size=20,
                                color="#6B4423",
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.W_500,
                                font_family="Newsreader",
                            ),
                            margin=ft.margin.only(bottom=70),
                        ),

                        ft.Container(
                            content=ft.ElevatedButton(
                                text="Get Started",
                                color="#FFFFFF",
                                bgcolor="#A0522D",
                                width=220,
                                height=55,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    elevation=0,
                                    side=ft.BorderSide(2, "#4D3322"),
                                    text_style=ft.TextStyle(
                                        size=18,
                                        weight=ft.FontWeight.W_600,
                                        font_family="Newsreader",
                                    ),
                                ),
                                on_click=lambda _: on_get_started_click(page),
                            ),
                            alignment=ft.alignment.center,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),

                ft.Container(
                    height=10,
                    bgcolor="#4A2C17",
                    width=float("inf"),
                ),
                
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("Wardatul Khoiroh", size=14, color="#4A2C17", font_family="Newsreader", weight=ft.FontWeight.W_500),
                            ft.Text("Ranashahira Reztaputri", size=14, color="#4A2C17", font_family="Newsreader", weight=ft.FontWeight.W_500),
                            ft.Text("Diyah Susan Nugrahani", size=14, color="#4A2C17", font_family="Newsreader", weight=ft.FontWeight.W_500),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(vertical=15, horizontal=50),
                ),
            ],
            spacing=0, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    
    return welcome_container

def on_get_started_click(page: ft.Page):
    page.controls.clear()
    search_cv_container = create_search_cv_page(page)
    page.add(search_cv_container)
    page.update()