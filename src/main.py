import flet as ft
from gui.landing_page import create_landing_page

def main(page: ft.Page):
    page.fonts = {
        "Newsreader": "fonts/Newsreader-VariableFont_opsz,wght.ttf"
    }

    page.theme = ft.Theme(font_family="Newsreader")
    page.title = "ScoopyHire"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    welcome_view = create_landing_page(page)
    page.add(welcome_view)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")

