import flet as ft
from .search_cv import create_search_cv_page

def create_landing_page(page: ft.Page):
    """
    Membuat halaman welcome ScoopyHire
    """
    
    # Container utama dengan background gradient coklat
    welcome_container = ft.Container(
        content=ft.Column(
            [
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
                                "Welcome to",
                                size=24,
                                color="#8B4513",
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.W_400,
                            ),
                            ft.Text(
                                "ScoopyHire",
                                size=64,
                                color="#5D2E0A",
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    margin=ft.margin.only(top=100, bottom=50),
                ),
                
                # Subtitle/tagline
                ft.Container(
                    content=ft.Text(
                        "Stop guessing. Start matching. ScoopyHire gets the CVs\nyou need.",
                        size=18,
                        color="#6B4423",
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_400,
                    ),
                    margin=ft.margin.only(bottom=60),
                ),
                
                # Tombol Get Started
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Get Started",
                        bgcolor="#8B4513",
                        color="white",
                        width=200,
                        height=50,
                        style=ft.ButtonStyle(
                            text_style=ft.TextStyle(
                                size=18,
                                weight=ft.FontWeight.W_500,
                            ),
                            shape=ft.RoundedRectangleBorder(radius=2),
                            shadow_color="#4D3322",
                            elevation=3,
                        ),
                        on_click=lambda _: on_get_started_click(page),
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=50),
                ),
                
                # Spacer untuk mendorong footer ke bawah
                ft.Container(expand=True),
                
                # Footer dengan nama-nama
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("Wardatul Khoiroh", size=12, color="#8B4513"),
                            ft.Text("Ranashahira Reztaputri", size=12, color="#8B4513"),
                            ft.Text("Diyah Susan Nugrahani", size=12, color="#8B4513"),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=20),
                    bgcolor="#D2B48C",
                ),
                
                # Garis coklat tua di bagian bawah
                ft.Container(
                    height=8,
                    bgcolor="#4A2C17",
                    width=float("inf"),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#F5E6D3", "#E6D2B8"],
        ),
        expand=True,
    )
    
    return welcome_container

def on_get_started_click(page: ft.Page):
    """
    Handler ketika tombol Get Started diklik
    Navigasi ke halaman search CV
    """
    print("Get Started clicked!")
    
    # Hapus semua kontrol yang ada di halaman
    page.controls.clear()
    
    # Buat dan tambahkan halaman search CV
    search_cv_container = create_search_cv_page(page)
    page.add(search_cv_container)
    
    # Update tampilan halaman
    page.update()