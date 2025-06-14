import flet as ft
import os
import re
import time
import mysql.connector
from algorithms.boyer_moore import boyer_moore_search
from algorithms.kmp import kmp_search
from algorithms.ahocorasick import aho_corasick_search
from gui.summary import create_summary_page, load_applicant_by_exact_filename_from_db
from gui.pdf_view import show_cv_threaded
from collections import Counter


def create_search_cv_page(page: ft.Page):
    applicant_db = {}
    cv_mapping = {}
    pattern_files = []
    search_results = []
    selected_algorithm = "KMP"
    has_searched = False

    keywords_field = ft.TextField(
        hint_text="Enter your keywords (comma separated)...",
        border_color="#5D2E0A",
        border_width=2,
        bgcolor="#F0DABB",
        height=50,
        text_style=ft.TextStyle(color="#5D2E0A", size=16),
        hint_style=ft.TextStyle(color="#A08C7D", size=16),
        content_padding=ft.padding.symmetric(horizontal=15),
    )
    
    results_input = ft.TextField(
        hint_text="e.g. 10",
        value="10",
        width=120,
        height=45,
        border_color="#5D2E0A",
        border_width=2,
        bgcolor="#F0DABB",
        text_style=ft.TextStyle(color="#5D2E0A", size=16),
        hint_style=ft.TextStyle(color="#A08C7D", size=16),
        keyboard_type=ft.KeyboardType.NUMBER,
        content_padding=ft.padding.symmetric(horizontal=15)
    )
    
    def create_algorithm_button(name, is_selected=True):
        return ft.Container(
            content=ft.Text(
                name,
                color="#FFFFFF" if is_selected else "#5D2E0A",
                size=14,
                weight=ft.FontWeight.W_600,
            ),
            bgcolor="#8B4513" if is_selected else "transparent",
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border=ft.border.all(2, "#5D2E0A"),
            height=45,
            on_click=lambda e, alg=name: select_algorithm(alg),
        )
    
    kmp_button = create_algorithm_button("KMP", True)
    bm_button = create_algorithm_button("BM", False)
    ac_button = create_algorithm_button("AC", False)
    
    input_controls = [keywords_field, results_input, kmp_button, bm_button, ac_button]

    results_container = ft.Column(
        controls=[],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    search_button = ft.ElevatedButton(
        text="Search CV",
        bgcolor="#8B4513", 
        color="white",
        height=55,
        width=650, 
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(size=20, weight=ft.FontWeight.W_600),
            shape=ft.RoundedRectangleBorder(radius=0),
            elevation=0,
        ),
        on_click=lambda e: on_search_click(e),
    )
    
    def select_algorithm(algorithm):
        nonlocal selected_algorithm
        if has_searched:
            return
            
        selected_algorithm = algorithm
        
        for btn, name in [(kmp_button, "KMP"), (bm_button, "BM"), (ac_button, "AC")]:
            is_selected = algorithm == name
            btn.bgcolor = "#8B4513" if is_selected else "transparent"
            btn.content.color = "white" if is_selected else "#5D2E0A"
        page.update()
    
    def reset_search_state():
        nonlocal has_searched
        has_searched = False

        for control in input_controls:
            control.disabled = False
        
        keywords_field.value = ""
        results_input.value = "10"
        select_algorithm("KMP")
        
        search_button.text = "Search CV"
        search_button.bgcolor = "#8B4513"
        search_button.width = 650 
        
        results_container.controls.clear()
        page.update()

    def update_results_display(results, exact_time_ms, fuzzy_time_ms, cv_count):
        nonlocal has_searched
        results_container.controls.clear()
        
        if results:
            results_header = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                    )
                ]
            )
            
            results_grid = ft.Row(
                [create_result_card(result) for result in results],
                alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=20, run_spacing=20
            )
            results_container.controls.extend([results_header, ft.Container(height=30), results_grid])
        else:
            results_container.controls.append(ft.Text("No Results Found", size=24, color="#5D2E0A"))
            
        has_searched = True

        for control in input_controls:
            control.disabled = True
            
        search_button.text = "Search Again"
        search_button.bgcolor = "#6B421C"
        search_button.width = 650 
        page.update()
    
    def on_search_click(e):
        nonlocal has_searched
        if has_searched:
            reset_search_state()
            return
        
        keywords_input = keywords_field.value.strip()
        if not keywords_input:
            page.open(ft.SnackBar(content=ft.Text("Please enter keywords to search!")))
            return
            
        max_results_value = int(results_input.value) if results_input.value.strip().isdigit() else 10
        
        search_data = search_keywords(keywords_input, selected_algorithm.lower(), max_results_value)
        update_results_display(search_data["results"], search_data["exact_time_ms"], search_data["fuzzy_time_ms"], search_data["cv_count"])
    
    def search_with_algorithm(text, keyword, algorithm='kmp'):
        if algorithm.lower() == 'kmp':
            return kmp_search(text, keyword)
        elif algorithm.lower() in ['boyer-moore', 'bm']:
            return boyer_moore_search(text, keyword)
        elif algorithm.lower() in ['ahocorasick', 'ac']:
            matches = aho_corasick_search(text, [keyword])
            return [start for pattern, start, end in matches if pattern == keyword]
        else:
            return []

    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def fuzzy_search(text, keyword, max_distance=1):
        words = re.findall(r'\b\w+\b', text.lower())
        keyword_lower = keyword.lower()
        found_words_counter = Counter()
        for word in words:
            if levenshtein_distance(word, keyword_lower) <= max_distance:
                found_words_counter[word] += 1
        return dict(found_words_counter)

    def get_applicant_name_by_cv(filename):
        DB_CONFIG = { "host": "localhost", "user": "ats_user", "password": "Ats_Pass11", "database": "cv_ats"}
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            clean_filename = filename.replace(".txt", "")
            query = """
            SELECT ap.first_name, ap.last_name, ad.application_role
            FROM ApplicantProfile ap JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
            WHERE REPLACE(SUBSTRING_INDEX(ad.cv_path, '/', -1), '.pdf', '') = %s LIMIT 1;
            """
            cursor.execute(query, (clean_filename,))
            result = cursor.fetchone()
            if result:
                return f"{result['first_name']} {result['last_name']}", result['application_role']
            return f"Unknown: {filename}", "N/A"
        except Exception as e:
            print(f"DB Error in get_applicant_name_by_cv: {e}")
            return f"Unknown: {filename}", "N/A"
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def search_keywords(keywords_input, algorithm, max_results_count):
        if not pattern_files:
            return {"results": [], "exact_time_ms": 0, "fuzzy_time_ms": 0, "cv_count": 0}

        keywords = [kw.strip().lower() for kw in keywords_input.split(',') if kw.strip()]
        if not keywords:
            return {"results": [], "exact_time_ms": 0, "fuzzy_time_ms": 0, "cv_count": len(pattern_files)}
        
        results = []
        
        exact_start_time = time.time()
        for filename, text in pattern_files:
            text_lower = text.lower()
            keyword_results = {}
            total_matches = 0
            for keyword in keywords:
                positions = search_with_algorithm(text_lower, keyword, algorithm)
                if positions:
                    if keyword not in keyword_results:
                        keyword_results[keyword] = {'count': 0, 'type': 'exact'}
                    keyword_results[keyword]['count'] += len(positions)
                    total_matches += len(positions)
            if keyword_results:
                name, role = get_applicant_name_by_cv(filename)
                results.append({"name": name, "role": role, "filename": filename, "total_matches": total_matches, "keyword_details": keyword_results, "match_type": "exact"})
        
        exact_time_ms = int((time.time() - exact_start_time) * 1000)

        keywords_for_fuzzy = keywords
        fuzzy_time_ms = 0

        if keywords_for_fuzzy:
            fuzzy_start_time = time.time()
            for filename, text in pattern_files:
                text_lower = text.lower()
                
                all_fuzzy_matches_for_cv = {}
                total_fuzzy_matches_for_cv = 0

                for keyword in keywords_for_fuzzy:
                    found_matches = fuzzy_search(text_lower, keyword)
                    
                    if found_matches:
                        for found_word, count in found_matches.items():
                            if found_word == keyword:
                                continue
                            
                            if found_word not in all_fuzzy_matches_for_cv:
                                all_fuzzy_matches_for_cv[found_word] = {'count': 0, 'type': 'fuzzy'}
                            all_fuzzy_matches_for_cv[found_word]['count'] += count
                            total_fuzzy_matches_for_cv += count

                if all_fuzzy_matches_for_cv:
                    existing_result = next((r for r in results if r['filename'] == filename), None)
                    if existing_result:
                        for word, details in all_fuzzy_matches_for_cv.items():
                            if word in existing_result['keyword_details']:
                                existing_result['keyword_details'][word]['count'] += details['count']
                            else:
                                existing_result['keyword_details'][word] = details
                        existing_result['total_matches'] += total_fuzzy_matches_for_cv
                        existing_result['match_type'] = 'mixed'
                    else:
                        name, role = get_applicant_name_by_cv(filename)
                        results.append({"name": name, "role": role, "filename": filename, "total_matches": total_fuzzy_matches_for_cv, "keyword_details": all_fuzzy_matches_for_cv, "match_type": "fuzzy"})
            fuzzy_time_ms = int((time.time() - fuzzy_start_time) * 1000)

        results.sort(key=lambda x: x["total_matches"], reverse=True)
        if max_results_count > 0:
            results = results[:max_results_count]
        
        return {"results": results, "exact_time_ms": exact_time_ms, "fuzzy_time_ms": fuzzy_time_ms, "cv_count": len(pattern_files)}

    def create_result_card(result):
        match_type = result.get("match_type", "exact")
        if match_type == "exact":
            match_type_text = "Exact Match"
            match_type_color = "#2E7D32"
        elif match_type == "fuzzy":
            match_type_text = "Fuzzy Match"
            match_type_color = "#FF8F00"
        else:
            match_type_text = "Mixed Match"
            match_type_color = "#1976D2"

        def show_summary_view(e):
            summary_view = create_summary_page(result, lambda ev: go_back_to_search(summary_view))
            search_container.visible = False
            page.add(summary_view)
            page.update()

        def go_back_to_search(summary_view):
            if summary_view in page.controls:
                page.controls.remove(summary_view)
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
                keyword_details_display.append(
                    ft.Text(f"{i+1}. {keyword.capitalize()}{detail_type}: {details['count']} occurences", size=14, color="#5D2E0A")
                )

        return ft.Container(
            width=350,
            border=ft.border.all(2, "#5D2E0A"),
            padding=0,
            bgcolor="#DFCAAD",
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
                                    bgcolor=match_type_color,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12,
                                ),
                            ]
                        )
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=15, vertical=10),
                        content=ft.Column(
                            [
                                ft.Text("Matched keywords:", size=16, weight=ft.FontWeight.W_500, color="#5D2E0A"),
                                *keyword_details_display
                            ],
                            spacing=5,
                        )
                    ),
                    ft.Container(
                        bgcolor="#5A4935",
                        padding=ft.padding.symmetric(horizontal=5, vertical=2),
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

    def load_all_data():
        nonlocal pattern_files
        folder_path = "data/pattern_matching" if os.path.exists("data/pattern_matching") else "pattern_matching"
        if not os.path.exists(folder_path):
            print("Pattern matching folder not found")
            return
        try:
            for filename in os.listdir(folder_path):
                if filename.endswith('.txt'):
                    with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                        pattern_files.append((filename, f.read()))
            print(f"Loaded {len(pattern_files)} pattern files")
        except Exception as e:
            print(f"Error loading data: {e}")

    load_all_data()

    search_container = ft.Container(
        expand=True,
        bgcolor="#F6E7D0",
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=10, bgcolor="#4A2C17", width=float("inf")),
                ft.Container(
                    content=ft.Column([
                        ft.Text("ScoopyHire", size=48, color="#5D2E0A", weight=ft.FontWeight.BOLD),
                        ft.Container(height=2, bgcolor="#5D2E0A", width=300, margin=ft.margin.symmetric(vertical=5)),
                        ft.Row([ft.Text(c, size=14, color="#5D2E0A") for c in "CV ANALYZER APP"], alignment=ft.MainAxisAlignment.CENTER, spacing=3)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    margin=ft.margin.only(top=30, bottom=40),
                ),
                
                ft.Column(
                    width=650,
                    spacing=20,
                    controls=[
                        ft.Column([ft.Text("Keywords", size=20, weight=ft.FontWeight.BOLD, color="#5D2E0A"), keywords_field], spacing=10),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
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