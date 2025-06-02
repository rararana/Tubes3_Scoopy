import flet as ft

def create_search_cv_page(page: ft.Page):
    """
    Membuat halaman pencarian CV ScoopyHire
    """
    
    # Sample data untuk hasil pencarian
    search_results = [
        {
            "name": "Wardes",
            "matches": 4,
            "keywords": [
                "React: ... occurences",
                "Express : .. occurences", 
                "HTML : .. occurences"
            ]
        },
        {
            "name": "Rana",
            "matches": 3,
            "keywords": [
                "React: ... occurences",
                "Express : .. occurences",
                "HTML : .. occurences"
            ]
        },
        {
            "name": "Diyah",
            "matches": 2,
            "keywords": [
                "React: ... occurences",
                "Express : .. occurences",
                "HTML : .. occurences"
            ]
        }
    ]
    
    def create_result_card(result):
        """Membuat card untuk hasil pencarian"""
        return ft.Container(
            content=ft.Column(
                [
                    # Header card dengan nama dan jumlah match
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    result["name"],
                                    size=24,
                                    color="#5D2E0A",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"{result['matches']} matches",
                                    size=16,
                                    color="#8B4513",
                                    weight=ft.FontWeight.W_400,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        margin=ft.margin.only(bottom=15),
                    ),
                    
                    # Matched keywords section
                    ft.Text(
                        "Matched keywords:",
                        size=14,
                        color="#6B4423",
                        weight=ft.FontWeight.W_500,
                    ),
                    
                    # List keywords
                    ft.Column(
                        [
                            ft.Text(
                                f"{i+1}. {keyword}",
                                size=14,
                                color="#6B4423",
                            )
                            for i, keyword in enumerate(result["keywords"])
                        ],
                        spacing=5,
                    ),
                    
                    # Spacer
                    ft.Container(height=20),
                    
                    # Footer buttons
                    ft.Row(
                        [
                            ft.TextButton(
                                text="< Summary",
                                style=ft.ButtonStyle(
                                    color="#F5E6D3",
                                ),
                            ),
                            ft.TextButton(
                                text="View CV >",
                                style=ft.ButtonStyle(
                                    color="#F5E6D3",
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=5,
            ),
            bgcolor="#D2B48C",
            padding=20,
            border_radius=8,
            margin=ft.margin.only(bottom=20),
            width=350,
        )
    
    # Container utama dengan scrollable content
    search_container = ft.Container(
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
                                "ScoopyHire",
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
                                "CV ANALYZER APP",
                                size=14,
                                color="#5D2E0A",
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.W_400,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    margin=ft.margin.only(top=30, bottom=40),
                ),
                
                # Keywords input section
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Keywords",
                                size=18,
                                color="#5D2E0A",
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.TextField(
                                hint_text="Enter your keywords...",
                                bgcolor="#F5E6D3",
                                border_color="#8B4513",
                                width=400,
                                height=50,
                                text_style=ft.TextStyle(
                                    color="#5D2E0A",
                                    size=14,
                                ),
                                hint_style=ft.TextStyle(
                                    color="#8B8B8B",
                                    size=14,
                                ),
                            ),
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=30),
                ),
                
                # Algorithm and Results selection row
                ft.Container(
                    content=ft.Row(
                        [
                            # Algorithm selection
                            ft.Column(
                                [
                                    ft.Text(
                                        "Choose your preferred algorithm",
                                        size=16,
                                        color="#5D2E0A",
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Container(
                                                content=ft.Text(
                                                    "KMP",
                                                    color="white",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500,
                                                ),
                                                bgcolor="#8B4513",
                                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                                border_radius=4,
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    "BM",
                                                    color="#5D2E0A",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500,
                                                ),
                                                bgcolor="#F5E6D3",
                                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                                border_radius=4,
                                                border=ft.border.all(1, "#8B4513"),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    "AC",
                                                    color="#5D2E0A",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500,
                                                ),
                                                bgcolor="#F5E6D3",
                                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                                border_radius=4,
                                                border=ft.border.all(1, "#8B4513"),
                                            ),
                                        ],
                                        spacing=5,
                                    ),
                                ],
                                spacing=10,
                            ),
                            
                            # Results count selection
                            ft.Column(
                                [
                                    ft.Text(
                                        "Top results to show",
                                        size=16,
                                        color="#5D2E0A",
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Dropdown(
                                        width=120,
                                        #height=40,
                                        bgcolor="#F5E6D3",
                                        border_color="#8B4513",
                                        hint_text="e.g. 10",
                                        options=[
                                            ft.dropdown.Option("5"),
                                            ft.dropdown.Option("10"),
                                            ft.dropdown.Option("15"),
                                            ft.dropdown.Option("20"),
                                        ],
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    margin=ft.margin.only(bottom=30),
                    width=400,
                ),
                
                # Search button
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Search CV",
                        bgcolor="#8B4513",
                        color="white",
                        width=400,
                        height=50,
                        style=ft.ButtonStyle(
                            text_style=ft.TextStyle(
                                size=18,
                                weight=ft.FontWeight.W_500,
                            ),
                            shape=ft.RoundedRectangleBorder(radius=4),
                            shadow_color="#4D3322",
                            elevation=4,
                        ),
                        on_click=lambda _: on_search_click(page),
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=40),
                ),
                
                # Results section
                ft.Container(
                    content=ft.Column(
                        [
                            # Results header with lines
                            ft.Row(
                                [
                                    ft.Container(
                                        height=2,
                                        bgcolor="#5D2E0A",
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            "Found 100 Results",
                                            size=24,
                                            color="#5D2E0A",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        padding=ft.padding.symmetric(horizontal=20),
                                    ),
                                    ft.Container(
                                        height=2,
                                        bgcolor="#5D2E0A",
                                        expand=True,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            
                            # Scan time
                            ft.Container(
                                content=ft.Text(
                                    "Scanned in 100 ms",
                                    size=14,
                                    color="#8B4513",
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                margin=ft.margin.only(top=10, bottom=30),
                            ),
                            
                            # Results grid
                            ft.Row(
                                [
                                    create_result_card(result)
                                    for result in search_results
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                wrap=True,
                                spacing=20,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    margin=ft.margin.only(bottom=40),
                ),
                
                # Garis coklat tua di bagian bawah
                ft.Container(
                    height=8,
                    bgcolor="#4A2C17",
                    width=float("inf"),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,  # Membuat halaman scrollable
        ),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#F5E6D3", "#E6D2B8"],
        ),
        expand=True,
    )
    
    return search_container

def on_search_click(page: ft.Page):
    """
    Handler ketika tombol Search CV diklik
    """
    print("Search CV clicked!")
    # Implementasi logika pencarian di sini
    pass

# def main(page: ft.Page):
#     """
#     Main function untuk testing halaman
#     """
#     page.title = "ScoopyHire - Search CV"
#     page.window_width = 800
#     page.window_height = 600
#     page.padding = 0
#     page.spacing = 0
    
#     page.add(create_search_cv_page(page))

# if __name__ == "__main__":
#     ft.app(target=main)