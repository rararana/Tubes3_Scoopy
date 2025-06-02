import flet as ft
from gui.landing_page import create_landing_page

def main(page: ft.Page):
    page.title = "ScoopyHire"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    
    # Setup routing atau navigation manager di sini
    welcome_view = create_landing_page(page)
    page.add(welcome_view)

if __name__ == "__main__":
    ft.app(target=main)