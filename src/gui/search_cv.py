import flet as ft
import os
import re
import time
import mysql.connector
from collections import defaultdict
from algorithms.boyer_moore import boyer_moore_search
from algorithms.kmp import kmp_search
from algorithms.ahocorasick import AhoCorasick, aho_corasick_search
from gui.summary import create_summary_page
from gui.summary import load_applicant_by_exact_filename_from_db

from gui.pdf_view import show_cv_threaded, show_pdf_info
    

    
def create_search_cv_page(page: ft.Page):
    """
    Membuat halaman pencarian CV ScoopyHire dengan data sebenarnya
    """
    applicant_db = {}
    cv_mapping = {}
    pattern_files = []
    search_results = []
    selected_algorithm = "KMP"
    max_results = 10
    has_searched = False  # to track if search has been performed
    
    keywords_field = ft.TextField(
        hint_text="Enter your keywords (comma separated)...",
        bgcolor="#F5E6D3",
        border_color="#8B4513",
        width=420,
        height=50,
        text_style=ft.TextStyle(color="#5D2E0A", size=14),
        hint_style=ft.TextStyle(color="#8B8B8B", size=14),
    )
    
    results_input = ft.TextField(
        hint_text="10",
        value="10",
        width=120,
        height=40,
        bgcolor="#F5E6D3",
        border_color="#8B4513",
        text_style=ft.TextStyle(color="#5D2E0A", size=14),
        hint_style=ft.TextStyle(color="#8B8B8B", size=14),
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    
    def create_algorithm_button(name, is_selected=True):
        return ft.Container(
            content=ft.Text(
                name,
                color="white" if is_selected else "#5D2E0A",
                size=14,
                weight=ft.FontWeight.W_500,
            ),
            bgcolor="#8B4513" if is_selected else "#F5E6D3",
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border_radius=4,
            border=None if is_selected else ft.border.all(1, "#8B4513"),
            height=40,
            on_click=lambda e, alg=name: select_algorithm(alg),
        )
    
    kmp_button = create_algorithm_button("KMP", True)
    bm_button = create_algorithm_button("BM", False)
    ac_button = create_algorithm_button("AC", False)
    
    results_container = ft.Column(
        controls=[],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    search_button = ft.ElevatedButton(
        text="Search CV",
        bgcolor="#8B4513",
        color="white",
        width=420,
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
        on_click=lambda e: on_search_click(e),
    )
    
    def select_algorithm(algorithm):
        nonlocal selected_algorithm
        selected_algorithm = algorithm
        
        kmp_button.bgcolor = "#8B4513" if algorithm == "KMP" else "#F5E6D3"
        kmp_button.content.color = "white" if algorithm == "KMP" else "#5D2E0A"
        kmp_button.border = None if algorithm == "KMP" else ft.border.all(1, "#8B4513")
        
        bm_button.bgcolor = "#8B4513" if algorithm == "BM" else "#F5E6D3"
        bm_button.content.color = "white" if algorithm == "BM" else "#5D2E0A"
        bm_button.border = None if algorithm == "BM" else ft.border.all(1, "#8B4513")
        
        ac_button.bgcolor = "#8B4513" if algorithm == "AC" else "#F5E6D3"
        ac_button.content.color = "white" if algorithm == "AC" else "#5D2E0A"
        ac_button.border = None if algorithm == "AC" else ft.border.all(1, "#8B4513")
        
        page.update()
    
    def reset_search_state():
        nonlocal has_searched, search_results, selected_algorithm

        has_searched = False
        search_results = []

        keywords_field.value = ""
        results_input.value = "10"

        selected_algorithm = "KMP"
        select_algorithm("KMP")
        search_button.text = "Search CV"
        
        results_container.controls.clear()
        
        page.update()
    
    def load_database_from_sql():
        """Load applicant data from init_db.sql file"""
        nonlocal applicant_db, cv_mapping
        
        print("Loading database...")
        
        possible_sql_paths = ["src/database/init_db.sql", "database/init_db.sql", "init_db.sql"]
        
        sql_file = None
        for path in possible_sql_paths:
            if os.path.exists(path):
                sql_file = path
                break
        
        if not sql_file:
            print("File init_db.sql tidak ditemukan!")
            return False
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            profile_pattern = r"INSERT INTO ApplicantProfile.*?VALUES\s*(.*?)(?=INSERT|$)"
            profile_match = re.search(profile_pattern, content, re.DOTALL)
            
            if profile_match:
                values_text = profile_match.group(1)
                row_pattern = r"\(\s*(\d+),\s*'([^']+)',\s*'([^']+)',\s*'[^']*',\s*'[^']*'\)"
                rows = re.findall(row_pattern, values_text)
                
                for applicant_id, first_name, last_name in rows:
                    applicant_db[int(applicant_id)] = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'full_name': f"{first_name} {last_name}"
                    }
            
            detail_pattern = r"INSERT INTO ApplicationDetail.*?VALUES\s*(.*?)(?=INSERT|$)"
            detail_matches = re.findall(detail_pattern, content, re.DOTALL)
            
            for match in detail_matches:
                row_pattern = r"\(\s*(\d+),\s*'([^']+)',\s*'[^']*?/([^/]+?)\.pdf'\)"
                rows = re.findall(row_pattern, match)
                
                for applicant_id, role, filename in rows:
                    applicant_id_int = int(applicant_id)
                    cv_mapping[filename] = {
                        'applicant_id': applicant_id_int,
                        'role': role
                    }
                    
                    if applicant_id_int not in applicant_db:
                        applicant_db[applicant_id_int] = {
                            'first_name': f'Applicant_{applicant_id_int}',
                            'last_name': '',
                            'full_name': f'Applicant_{applicant_id_int}'
                        }
            
            print(f"Loaded {len(applicant_db)} applicants and {len(cv_mapping)} CV mappings")
            return True
            
        except Exception as e:
            print(f"Error loading database: {e}")
            return False
    
    def load_pattern_files():
        """Load all pattern matching text files"""
        nonlocal pattern_files
        
        possible_folders = ["data/pattern_matching", "pattern_matching"]
        
        folder_path = None
        for path in possible_folders:
            if os.path.exists(path):
                folder_path = path
                break
        
        if not folder_path:
            print("Folder pattern_matching tidak ditemukan!")
            return False
        
        pattern_files = []
        try:
            txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
            
            for filename in txt_files:
                path = os.path.join(folder_path, filename)
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    pattern_files.append((filename, text))
            
            print(f"Loaded {len(pattern_files)} pattern files")
            return True
            
        except Exception as e:
            print(f"Error loading pattern files: {e}")
            return False
    
    def search_with_algorithm(text, keyword, algorithm='kmp'):
        """Search keyword in text using specified algorithm"""
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
        """Calculate Levenshtein distance between two strings"""
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
    
    def fuzzy_search(text, keyword, max_distance=2):
        """Perform fuzzy search using Levenshtein distance"""
        words = re.findall(r'\b\w+\b', text.lower())
        keyword_lower = keyword.lower()
        matches = []
        
        for i, word in enumerate(words):
            if levenshtein_distance(word, keyword_lower) <= max_distance:
                word_pattern = r'\b' + re.escape(word) + r'\b'
                for match in re.finditer(word_pattern, text.lower()):
                    matches.append(match.start())
        
        return matches
    
    def get_applicant_name_by_cv(filename):
        """Get applicant name from MySQL database by CV filename"""
        DB_CONFIG = {
            "host": "localhost",
            "user": "ats_user",
            "password": "Ats_Pass11",
            "database": "cv_ats"
        }
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            clean_filename = filename.replace(".txt", "")
            
            query = """
            SELECT
                ap.first_name,
                ap.last_name,
                ad.application_role
            FROM
                ApplicantProfile ap
            JOIN
                ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
            WHERE
                REPLACE(SUBSTRING_INDEX(ad.cv_path, '/', -1), '.pdf', '') = %s
            LIMIT 1;
            """
            
            cursor.execute(query, (clean_filename,))
            result = cursor.fetchone()
            
            if result:
                full_name = f"{result['first_name']} {result['last_name']}"
                role = result['application_role']
                return f"{full_name} ({role})"
            else:
                return f"Unknown ({filename})"
                
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return f"Unknown ({filename})"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"Unknown ({filename})"
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
    
    def search_keywords(keywords_input, algorithm, max_results_count):
        """Main search function with exact and fuzzy matching"""
        if not pattern_files:
            return {
                "results": [],
                "exact_time_ms": 0,
                "fuzzy_time_ms": 0,
                "cv_count": 0
            }

        keywords = [kw.strip().lower() for kw in keywords_input.split(',') if kw.strip()]
        if not keywords:
            return {
                "results": [],
                "exact_time_ms": 0,
                "fuzzy_time_ms": 0,
                "cv_count": len(pattern_files)
            }
        
        algorithm_map = {'KMP': 'kmp', 'BM': 'bm', 'AC': 'ac'}
        algo_code = algorithm_map.get(algorithm, 'kmp')
        
        results = []
        
        print(f"Performing exact matching with {algorithm}...")
        exact_start_time = time.time()
        
        for filename, text in pattern_files:
            text_lower = text.lower()
            keyword_results = {}
            total_matches = 0
            
            for keyword in keywords:
                positions = search_with_algorithm(text_lower, keyword, algo_code)
                if positions:
                    keyword_results[keyword] = {
                        'count': len(positions),
                        'positions': positions[:3],
                        'type': 'exact'
                    }
                    total_matches += len(positions)
            
            if keyword_results:
                name = get_applicant_name_by_cv(filename)
                results.append({
                    "name": name,
                    "filename": filename,
                    "total_matches": total_matches,
                    "keywords_found": len(keyword_results),
                    "keyword_details": keyword_results,
                    "match_type": "exact"
                })

        exact_end_time = time.time()
        exact_time_ms = int((exact_end_time - exact_start_time) * 1000)

        exact_keywords = set()
        for result in results:
            exact_keywords.update(result['keyword_details'].keys())
        
        fuzzy_keywords = [kw for kw in keywords if kw not in exact_keywords]
        fuzzy_time_ms = 0
        
        if fuzzy_keywords:
            print(f"Performing fuzzy matching for: {', '.join(fuzzy_keywords)}")
            fuzzy_start_time = time.time()
            
            fuzzy_results = []
            for filename, text in pattern_files:
                text_lower = text.lower()
                fuzzy_keyword_results = {}
                fuzzy_total_matches = 0
                
                for keyword in fuzzy_keywords:
                    fuzzy_positions = fuzzy_search(text_lower, keyword, max_distance=2)
                    if fuzzy_positions:
                        fuzzy_keyword_results[keyword] = {
                            'count': len(fuzzy_positions),
                            'positions': fuzzy_positions[:3],
                            'type': 'fuzzy'
                        }
                        fuzzy_total_matches += len(fuzzy_positions)
                
                if fuzzy_keyword_results:
                    name = get_applicant_name_by_cv(filename)
                    
                    existing_result = None
                    for result in results:
                        if result['filename'] == filename:
                            existing_result = result
                            break
                    
                    if existing_result:
                        existing_result['keyword_details'].update(fuzzy_keyword_results)
                        existing_result['total_matches'] += fuzzy_total_matches
                        existing_result['keywords_found'] += len(fuzzy_keyword_results)
                        existing_result['match_type'] = 'mixed'
                    else:
                        fuzzy_results.append({
                            "name": name,
                            "filename": filename,
                            "total_matches": fuzzy_total_matches,
                            "keywords_found": len(fuzzy_keyword_results),
                            "keyword_details": fuzzy_keyword_results,
                            "match_type": "fuzzy"
                        })
            
            results.extend(fuzzy_results)
            fuzzy_end_time = time.time()
            fuzzy_time_ms = int((fuzzy_end_time - fuzzy_start_time) * 1000)

        results.sort(key=lambda x: (x["keywords_found"], x["total_matches"]), reverse=True)
        
        if max_results_count and max_results_count > 0:
            results = results[:max_results_count]
        
        return {
            "results": results,
            "exact_time_ms": exact_time_ms,
            "fuzzy_time_ms": fuzzy_time_ms,
            "cv_count": len(pattern_files)
        }

    def create_result_card(result):
        """Create card for search result"""
        match_type_color = "#2E7D32" if result["match_type"] == "exact" else "#FF8F00" if result["match_type"] == "fuzzy" else "#1976D2"
        match_type_text = "Exact Match" if result["match_type"] == "exact" else "Fuzzy Match" if result["match_type"] == "fuzzy" else "Mixed Match"
        
        path = result["filename"]
        path_without_extension = os.path.splitext(path)[0]
        profile_data = load_applicant_by_exact_filename_from_db(path_without_extension)
        
        cv_path = profile_data.get("cv_path", "") if profile_data else ""
        
        def safe_show_cv(e):
            """Safely show CV with error handling and user feedback"""
            if cv_path and os.path.exists(cv_path):
                try:
                    page.open(ft.SnackBar(
                        content=ft.Text("Opening PDF... Please wait")
                    ))
                    
                    from gui.pdf_view import check_pdf_viewers_available
                    available_viewers = check_pdf_viewers_available()
                    
                    if available_viewers:
                        print(f"Available PDF viewers: {', '.join(available_viewers)}")
                        show_cv_threaded(cv_path)
                        
                        page.open(ft.SnackBar(
                            content=ft.Text(f"PDF opened with {available_viewers[0]}")
                        ))
                    else:
                        print("No PDF viewers available, showing text preview in console")
                        show_pdf_info(cv_path)
                        
                        page.open(ft.SnackBar(
                            content=ft.Text("No PDF viewer found. Check console for text preview.")
                        ))
                        
                except Exception as ex:
                    print(f"Error showing CV: {ex}")
                    show_pdf_info(cv_path)
                    
                    page.open(ft.SnackBar(
                        content=ft.Text("PDF viewer error. Check console for preview.")
                    ))
            else:
                page.open(ft.SnackBar(
                    content=ft.Text(f"CV file not found: {cv_path if cv_path else 'No path'}")
                ))
        keyword_details = []
        if 'keyword_details' in result:
            for keyword, details in result['keyword_details'].items():
                keyword_details.append(
                    ft.Row([
                        ft.Text(f"{keyword}", size=12, color="#5A4935", weight=ft.FontWeight.W_500),
                        ft.Text(f"{details['count']} matches", size=12, color="#8B4513")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Row(
                                [
                                    ft.Text(
                                        result["name"].split(' (')[0],
                                        size=20,
                                        color="#5D2E0A",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            match_type_text,
                                            size=10,
                                            color="white",
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        bgcolor=match_type_color,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=12,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                f"Role: {result['name'].split('(')[1].replace(')', '')}" if '(' in result["name"] else "",
                                size=12,
                                color="#8B4513",
                                weight=ft.FontWeight.W_400,
                            ),
                        ]),
                        margin=ft.margin.only(bottom=10),
                    ),
                    
                    ft.Row(
                        [
                            ft.Text(
                                f"{result['keywords_found']} keywords",
                                size=14,
                                color="#8B4513",
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                f"{result['total_matches']} total matches",
                                size=14,
                                color="#8B4513",
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    
                    ft.Container(height=10),
                    
                    ft.Text(
                        "Keywords found:",
                        size=14,
                        color="#6B4423",
                        weight=ft.FontWeight.W_500,
                    ),
                    
                    ft.Column(
                        keyword_details,
                        spacing=3,
                    ),
                    
                    ft.Container(height=15),
                    
                    ft.Row([
                    ft.TextButton(
                        text="View Details",
                        style=ft.ButtonStyle(color="#8B4513"),
                        on_click=lambda e: show_resume(result),
                    ),
                    ft.TextButton(
                        text="View CV",
                        style=ft.ButtonStyle(color="#8B4513"),
                        on_click=safe_show_cv,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=5),
            bgcolor="#D2B48C",
            padding=20,
            border_radius=8,
            margin=ft.margin.only(bottom=15),
            width=350,
        )
    
    def show_resume(result):
        print("Show Resume clicked!")
        
        def go_back_to_search():
            page.controls.clear()
            page.add(create_search_cv_page(page))
            page.update()
        
        page.controls.clear()
        
        summary_page = create_summary_page(result, on_back_click=go_back_to_search)
        page.add(summary_page)
        
        page.update()
    
    def update_results_display(results, exact_time_ms, fuzzy_time_ms, cv_count):
        """Update the results display"""
        nonlocal has_searched
        
        results_container.controls.clear()
        
        if results:
            results_header = ft.Row(
                [
                    ft.Container(
                        height=2,
                        bgcolor="#5D2E0A",
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            f"Found {len(results)} Results",
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
            )
            
            # Menentukan jumlah CV yang dipindai untuk fuzzy match
            fuzzy_cv_scanned = cv_count if fuzzy_time_ms > 0 else 0
            
            summary_items = [
                ft.Text(
                    f"Exact Match: {cv_count} CVs scanned in {exact_time_ms}ms.",
                    size=14,
                    color="#8B4513",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    f"Fuzzy Match: {fuzzy_cv_scanned} CVs scanned in {fuzzy_time_ms}ms.",
                    size=14,
                    color="#8B4513",
                    text_align=ft.TextAlign.CENTER,
                )
            ]

            summary_container = ft.Container(
                content=ft.Column(
                    summary_items,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                margin=ft.margin.only(top=10, bottom=20),
            )
            
            results_grid = ft.Row(
                [create_result_card(result) for result in results],
                alignment=ft.MainAxisAlignment.CENTER,
                wrap=True,
                spacing=20,
            )
            
            results_container.controls.extend([results_header, summary_container, results_grid])
        else:
            no_results = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "No Results Found",
                        size=24,
                        color="#5D2E0A",
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Try different keywords or check spelling",
                        size=14,
                        color="#8B4513",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=ft.margin.only(top=30, bottom=30),
            )
            results_container.controls.append(no_results)
        
        has_searched = True
        search_button.text = "Search Again"
        
        page.update()
    
    def on_search_click(e):
        """Handle search button click"""
        nonlocal has_searched
        
        if has_searched:
            reset_search_state()
            return
        
        keywords_input = keywords_field.value.strip()
        if not keywords_input:
            page.open(ft.SnackBar(content=ft.Text("Please enter keywords to search!")))
            return
        
        try:
            max_results_value = int(results_input.value) if results_input.value.strip() else 10
            if max_results_value <= 0:
                max_results_value = 10
        except ValueError:
            max_results_value = 10
            results_input.value = "10"
            page.update()

        if not applicant_db or not pattern_files:
            page.open(ft.SnackBar(content=ft.Text("Loading data...")))
            db_loaded = load_database_from_sql()
            files_loaded = load_pattern_files()
            
            if not db_loaded or not files_loaded:
                page.open(ft.SnackBar(content=ft.Text("Error loading data! Check file paths.")))
                return

        search_data = search_keywords(keywords_input, selected_algorithm, max_results_value)
        update_results_display(
            search_data["results"],
            search_data["exact_time_ms"],
            search_data["fuzzy_time_ms"],
            search_data["cv_count"]
        )
    
    search_container = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    height=8,
                    bgcolor="#4A2C17",
                    width=float("inf"),
                ),
                
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
                
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Keywords",
                                size=18,
                                color="#5D2E0A",
                                weight=ft.FontWeight.W_500,
                            ),
                            keywords_field,
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=30),
                ),
                
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        "Choose your preferred algorithm",
                                        size=16,
                                        color="#5D2E0A",
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Row(
                                        [kmp_button, bm_button, ac_button],
                                        spacing=5,
                                    ),
                                ],
                                spacing=10,
                            ),
                            
                            ft.Column(
                                [
                                    ft.Text(
                                        "Top results to show",
                                        size=16,
                                        color="#5D2E0A",
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    results_input,
                                ],
                                spacing=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    margin=ft.margin.only(bottom=30),
                    width=420,
                ),
                
                ft.Container(
                    content=search_button,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=40),
                ),
                
                results_container,
                
                ft.Container(
                    height=8,
                    bgcolor="#4A2C17",
                    width=float("inf"),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#F5E6D3", "#E6D2B8"],
        ),
        expand=True,
    )
    
    return search_container