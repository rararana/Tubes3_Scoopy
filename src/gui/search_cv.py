import flet as ft
import os

from services.search_service import search_keywords
from services.file_service import load_cv_text_files
from gui.summary import create_summary_page, load_applicant_by_exact_filename_from_db
from gui.pdf_view import show_cv_threaded

def create_search_cv_page(page: ft.Page):
    pattern_files = load_cv_text_files()
    selected_algorithm = "KMP"
    has_searched = False

    keywords_field = ft.TextField(
        hint_text="Enter your keywords (comma separated)...",
        border_color="#5D2E0A", border_width=2, bgcolor="#F0DABB", height=50,
        text_style=ft.TextStyle(color="#5D2E0A", size=16),
        hint_style=ft.TextStyle(color="#A08C7D", size=16),
        content_padding=ft.padding.symmetric(horizontal=15),
    )
    
    results_input = ft.TextField(
        value="10", width=120, height=45, border_color="#5D2E0A", border_width=2,
        bgcolor="#F0DABB", text_style=ft.TextStyle(color="#5D2E0A", size=16),
        hint_style=ft.TextStyle(color="#A08C7D", size=16),
        keyboard_type=ft.KeyboardType.NUMBER,
        content_padding=ft.padding.symmetric(horizontal=15)
    )
    
    def create_algorithm_button(name, is_selected=True):
        return ft.Container(
            content=ft.Text(name, color="#FFFFFF" if is_selected else "#5D2E0A", size=14, weight=ft.FontWeight.W_600),
            bgcolor="#8B4513" if is_selected else "#F0DABB",
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border=ft.border.all(2, "#5D2E0A"), height=45,
            on_click=lambda e, alg=name: select_algorithm(alg),
        )

    kmp_button = create_algorithm_button("KMP", True)
    bm_button = create_algorithm_button("BM", False)
    ac_button = create_algorithm_button("AC", False)
    
    algorithm_buttons = [kmp_button, bm_button, ac_button]
    input_controls = [keywords_field, results_input] + algorithm_buttons
    results_container = ft.Column(controls=[], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    search_button = ft.ElevatedButton(
        text="Search CV", bgcolor="#8B4513", color="white", height=55, width=650,
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(size=20, weight=ft.FontWeight.W_600),
            shape=ft.RoundedRectangleBorder(radius=0), elevation=0,
        ),
        on_click=lambda e: on_search_click(e),
    )
    
    def select_algorithm(algorithm):
        nonlocal selected_algorithm
        if has_searched: return
        
        selected_algorithm = algorithm
        for btn, name in [(kmp_button, "KMP"), (bm_button, "BM"), (ac_button, "AC")]:
            is_selected = algorithm == name
            btn.bgcolor = "#8B4513" if is_selected else "#F0DABB"
            btn.content.color = "white" if is_selected else "#5D2E0A"
        page.update()
    
    def reset_search_state():
        nonlocal has_searched
        has_searched = False
        for control in input_controls: control.disabled = False
        for btn in algorithm_buttons: btn.border = ft.border.all(2, "#5D2E0A")
        
        keywords_field.value = ""
        results_input.value = "10"
        select_algorithm("KMP")
        
        search_button.content = None
        search_button.text = "Search CV"
        search_button.bgcolor = "#8B4513"
        search_button.disabled = False
        
        results_container.controls.clear()
        page.update()

    def update_results_display(search_data):
        nonlocal has_searched
        results_container.controls.clear()
        
        results = search_data["results"]
        exact_time_ms = search_data["exact_time_ms"]
        fuzzy_time_ms = search_data["fuzzy_time_ms"]
        cv_count = search_data["cv_count"]
        
        if results:
            header = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(height=2, bgcolor="#5D2E0A", width=200),
                            ft.Container(
                                content=ft.Text(f"Found {len(results)} Results", size=24, color="#5D2E0A", weight=ft.FontWeight.BOLD),
                                margin=ft.margin.symmetric(horizontal=15)
                            ),
                            ft.Container(height=2, bgcolor="#5D2E0A", width=200),
                        ]
                    ),
                    ft.Column([
                        ft.Text(f"Exact Match: {cv_count} CVs scanned in {exact_time_ms}ms.", size=16, color="#8B4513"),
                        ft.Text(f"Fuzzy Match: {cv_count if fuzzy_time_ms > 0 else 0} CVs scanned in {fuzzy_time_ms}ms.", size=16, color="#8B4513")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
                ]
            )
            grid = ft.Row([create_result_card(result) for result in results], alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=20, run_spacing=20)
            results_container.controls.extend([header, ft.Container(height=30), grid])
        else:
            results_container.controls.append(ft.Text("No Results Found", size=24, color="#5D2E0A"))
            
        has_searched = True
        for control in input_controls:
            control.disabled = True
            if control in algorithm_buttons:
                control.border = ft.border.all(2, ft.Colors.with_opacity(0.4, "#8B4513"))
        
        search_button.content = None
        search_button.text = "Search Again"
        search_button.bgcolor = "#6B421C"
        search_button.disabled = False
        page.update()
    
    def on_search_click(e):
        nonlocal has_searched
        if has_searched:
            reset_search_state()
            return
        
        if not keywords_field.value.strip():
            page.open(ft.SnackBar(content=ft.Text("Please enter keywords to search!")))
            return

        search_button.disabled = True
        search_button.content = ft.Row(
            [ft.ProgressRing(width=20, height=20, stroke_width=2.5, color="white"),
             ft.Text("Searching, please wait...", size=20, weight=ft.FontWeight.W_600, color="white")],
            alignment=ft.MainAxisAlignment.CENTER, spacing=15
        )
        page.update()
            
        max_results_value = int(results_input.value) if results_input.value.strip().isdigit() else 10
        search_data = search_keywords(keywords_field.value, selected_algorithm.lower(), max_results_value, pattern_files)
        update_results_display(search_data)
    
    def create_result_card(result):
        match_type = result.get("match_type", "exact")
        if match_type == "exact": match_type_text, match_type_color = "Exact Match", "#2E7D32"
        elif match_type == "fuzzy": match_type_text, match_type_color = "Fuzzy Match", "#FF8F00"
        else: match_type_text, match_type_color = "Mixed Match", "#276DB1"

        def show_summary_view(e):
            summary_view = create_summary_page(result, lambda ev: go_back_to_search(summary_view))
            search_container.visible = False
            page.add(summary_view)
            page.update()

        def go_back_to_search(summary_view):
            if summary_view in page.controls: page.controls.remove(summary_view)
            search_container.visible = True
            page.update()

        def safe_show_cv(e):
            filename_no_ext = os.path.splitext(result["filename"])[0]
            profile_data = load_applicant_by_exact_filename_from_db(filename_no_ext)
            cv_path = profile_data.get("cv_path", "") if profile_data else ""
            if cv_path and os.path.exists(cv_path):
                show_cv_threaded(cv_path)
            else:
                page.open(ft.SnackBar(content=ft.Text(f"CV file not found: {cv_path or 'No path'}")))

        keyword_details_display = []
        if 'keyword_details' in result:
            for i, (keyword, details) in enumerate(result['keyword_details'].items()):
                detail_type = " (fuzzy)" if details.get('type') == 'fuzzy' else ""
                keyword_details_display.append(ft.Text(f"{i+1}. {keyword.capitalize()}{detail_type}: {details['count']} occurences", size=14, color="#5D2E0A"))

        return ft.Container(
            width=350, border=ft.border.all(2, "#5D2E0A"), padding=0, bgcolor="#DFCAAD",
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=15, vertical=10),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column([
                                    ft.Text(result.get("name", "Unknown"), size=20, weight=ft.FontWeight.BOLD, color="#5D2E0A"),
                                    ft.Text(f"{result.get('total_matches', 0)} total matches", size=14, color="#5D2E0A"),
                                ]),
                                ft.Container(
                                    content=ft.Text(match_type_text, size=10, color="white", weight=ft.FontWeight.W_500),
                                    bgcolor=match_type_color, padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12,
                                ),
                            ]
                        )
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=15, vertical=10),
                        content=ft.Column(
                            [ft.Text("Matched keywords:", size=16, weight=ft.FontWeight.W_500, color="#5D2E0A"), *keyword_details_display],
                            spacing=5
                        )
                    ),
                    ft.Container(
                        bgcolor="#5A4935", padding=ft.padding.symmetric(horizontal=5, vertical=2),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextButton("< Summary", on_click=show_summary_view, style=ft.ButtonStyle(color="white")),
                                ft.TextButton("View CV >", on_click=safe_show_cv, style=ft.ButtonStyle(color="white")),
                            ]
                        )
                    )
                ]
            )
        )

    search_container = ft.Container(
        expand=True, bgcolor="#F6E7D0",
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=10, bgcolor="#4A2C17", width=float("inf")),
                ft.Container(
                    content=ft.Column([
                        ft.Text("ScoopyHire", size=48, color="#5D2E0A", weight=ft.FontWeight.BOLD),
                        ft.Container(height=2, bgcolor="#5D2E0A", width=300, margin=ft.margin.symmetric(vertical=5)),
                        ft.Row([ft.Text(c, size=14, color="#5D2E0A") for c in "CV ANALYZER APP"], alignment=ft.MainAxisAlignment.CENTER, spacing=3)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    margin=ft.margin.only(top=30, bottom=40),
                ),
                ft.Column(
                    width=650, spacing=20,
                    controls=[
                        ft.Column([ft.Text("Keywords", size=20, weight=ft.FontWeight.BOLD, color="#5D2E0A"), keywords_field], spacing=10),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column([ft.Text("Choose your preferred algorithm", size=16, weight=ft.FontWeight.BOLD, color="#5D2E0A"), ft.Row([kmp_button, bm_button, ac_button], spacing=5)], spacing=10),
                                ft.Column([ft.Text("Top results to show", size=16, weight=ft.FontWeight.BOLD, color="#5D2E0A"), results_input], spacing=10)
                            ]
                        ),
                        search_button 
                    ]
                ),
                ft.Container(results_container, margin=ft.margin.symmetric(vertical=40)),
            ]
        )
    )
    
    return search_container