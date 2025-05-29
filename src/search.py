import os
import time
import json
import sys
import re
from collections import deque, defaultdict
from algorithms.boyer_moore import boyer_moore_search
from algorithms.kmp import kmp_search
from algorithms.ahocorasick import AhoCorasick, aho_corasick_search

# === LOAD DATABASE FROM SQL FILE ===
def load_database_from_sql():
    """Load applicant data from init_db.sql file"""
    applicant_db = {}
    cv_mapping = {}
    
    print("Starting database load...")
    
    # Coba berbagai lokasi file SQL
    possible_sql_paths = ["src/database/init_db.sql"]
    
    print("Checking SQL file locations:")
    for path in possible_sql_paths:
        exists = os.path.exists(path)
        print(f"   {path}: {'yes' if exists else 'no'}")
    
    sql_file = None
    for path in possible_sql_paths:
        if os.path.exists(path):
            sql_file = path
            break
    
    if not sql_file:
        print("File init_db.sql tidak ditemukan!")
        return {}, {}
    
    try:
        print(f"Reading SQL file: {sql_file}")
        with open(sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"SQL file size: {len(content)} characters")
        
        # Extract ApplicantProfile data
        print("Looking for ApplicantProfile data...")
        profile_pattern = r"INSERT INTO ApplicantProfile.*?VALUES\s*(.*?)(?=INSERT|$)"
        profile_match = re.search(profile_pattern, content, re.DOTALL)
        
        if profile_match:
            values_text = profile_match.group(1)
            print(f"ApplicantProfile values text length: {len(values_text)}")
            
            # Parse each row
            row_pattern = r"\(\s*(\d+),\s*'([^']+)',\s*'([^']+)',\s*'[^']*',\s*'[^']*'\)"
            rows = re.findall(row_pattern, values_text)
            
            print(f"Found {len(rows)} applicant profiles")
            
            for applicant_id, first_name, last_name in rows:
                applicant_db[int(applicant_id)] = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': f"{first_name} {last_name}"
                }
                
            # Print first few entries
            if applicant_db:
                print("Sample applicants loaded:")
                for i, (aid, data) in enumerate(list(applicant_db.items())[:3]):
                    print(f"   ID {aid}: {data['full_name']}")
        else:
            print("No ApplicantProfile INSERT statement found")
        
        # Extract ApplicationDetail data
        print("Looking for ApplicationDetail data...")
        detail_pattern = r"INSERT INTO ApplicationDetail.*?VALUES\s*(.*?)(?=INSERT|$)"
        detail_matches = re.findall(detail_pattern, content, re.DOTALL)
        
        print(f"Found {len(detail_matches)} ApplicationDetail blocks")
        
        total_mappings = 0
        missing_ids = set()
        
        for i, match in enumerate(detail_matches):
            # print(f"Processing block {i+1}, length: {len(match)}")
            
            # Parse each row
            row_pattern = r"\(\s*(\d+),\s*'([^']+)',\s*'[^']*?/([^/]+?)\.pdf'\)"
            rows = re.findall(row_pattern, match)
            
            # print(f"   Found {len(rows)} rows in this block")
            
            for applicant_id, role, filename in rows:
                applicant_id_int = int(applicant_id)
                cv_mapping[filename] = {
                    'applicant_id': applicant_id_int,
                    'role': role
                }
                total_mappings += 1
                
                # Check if applicant_id exists in applicant_db
                if applicant_id_int not in applicant_db:
                    missing_ids.add(applicant_id_int)
        
        print(f"Total CV mappings: {total_mappings}")
        print(f"Missing applicant IDs: {len(missing_ids)}")
        
        # Create mock entries for missing IDs
        if missing_ids:
            print("Creating mock entries for missing applicant IDs...")
            
            # Names pool for mock data
            first_names = ["John", "Sarah", "Michael", "Emily", "David", "Lisa", "James", "Anna", "Robert", "Maria",
                          "William", "Jennifer", "Richard", "Linda", "Charles", "Patricia", "Thomas", "Barbara", "Christopher", "Susan",
                          "Daniel", "Jessica", "Matthew", "Karen", "Anthony", "Nancy", "Mark", "Betty", "Donald", "Helen"]
            
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                         "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                         "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]
            
            for i, missing_id in enumerate(sorted(missing_ids)):
                first_name = first_names[i % len(first_names)]
                last_name = last_names[i % len(last_names)]
                
                applicant_db[missing_id] = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': f"{first_name} {last_name}"
                }
            
            print(f"Created {len(missing_ids)} mock applicant entries")
        
        # # Print sample CV mappings
        # if cv_mapping:
        #     print("Sample CV mappings:")
        #     for i, (filename, data) in enumerate(list(cv_mapping.items())[:5]):
        #         aid = data['applicant_id']
        #         name = applicant_db.get(aid, {}).get('full_name', f'ID_{aid}')
        #         print(f"   {filename}: {name} (ID {aid}, {data['role']})")
        
        return applicant_db, cv_mapping
        
    except Exception as e:
        print(f"Error reading SQL file: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

# === LOAD FILE-FILE PATTERN MATCHING ===
def load_pattern_files():
    """Load all pattern matching text files"""
    result = []
    
    print("Looking for pattern matching files...")
    
    # Coba berbagai kemungkinan lokasi folder pattern_matching
    possible_folders = ["data/pattern_matching"]
    
    print("Checking pattern_matching folders:")
    for path in possible_folders:
        exists = os.path.exists(path)
        print(f"   {path}: {'yes' if exists else 'no'}")
    
    folder_path = None
    for path in possible_folders:
        if os.path.exists(path):
            folder_path = path
            break
    
    if not folder_path:
        print("Folder pattern_matching tidak ditemukan!")
        return result
    
    print(f"Using folder: {os.path.abspath(folder_path)}")
    
    # List all files in folder
    all_files = os.listdir(folder_path)
    txt_files = [f for f in all_files if f.endswith('.txt')]
    
    print(f"Found {len(all_files)} total files, {len(txt_files)} .txt files")
    
    for filename in txt_files[:5]:  # Show first 5 files
        print(f"{filename}")
    
    if len(txt_files) > 5:
        print(f"   ... and {len(txt_files) - 5} more files")
    
    for filename in txt_files:
        path = os.path.join(folder_path, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                result.append((filename, text))
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    print(f"Loaded {len(result)} pattern files")
    return result

# === AMBIL NAMA KANDIDAT DARI DATABASE ===
def get_applicant_name_by_cv(applicant_db, cv_mapping, filename):
    """Get applicant name from database by CV filename"""
    if filename in cv_mapping:
        applicant_id = cv_mapping[filename]['applicant_id']
        role = cv_mapping[filename]['role']
        
        if applicant_id in applicant_db:
            applicant = applicant_db[applicant_id]
            return f"{applicant['full_name']} ({role})"
        else:
            return f"ID_{applicant_id} ({role})"
    
    return f"Unknown ({filename})"

# === GENERIC SEARCH FUNCTION ===
def search_with_algorithm(text, keyword, algorithm='kmp'):
    """
    Search keyword in text using specified algorithm
    Returns list of positions where keyword is found
    """
    if algorithm.lower() == 'kmp':
        return kmp_search(text, keyword)
    elif algorithm.lower() == 'boyer-moore' or algorithm.lower() == 'bm':
        return boyer_moore_search(text, keyword)
    elif algorithm.lower() == 'ahocorasick' or algorithm.lower() == 'aho':
        # For single keyword with Aho-Corasick, return just positions
        matches = aho_corasick_search(text, [keyword])
        return [start for pattern, start, end in matches if pattern == keyword]
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

# === PENCARIAN SINGLE KEYWORD ===
def search_keyword(keyword, files, applicant_db, cv_mapping, algorithm='kmp'):
    """Search keyword using specified algorithm"""
    result = []
    keyword_lower = keyword.lower()
    
    algorithm_name = get_algorithm_name(algorithm)
    print(f"Searching for '{keyword_lower}' using {algorithm_name} in {len(files)} files...")
    
    for filename, text in files:
        positions = search_with_algorithm(text.lower(), keyword_lower, algorithm)
        if positions:
            name = get_applicant_name_by_cv(applicant_db, cv_mapping, filename.replace(".txt", ""))
            result.append({
                "name": name,
                "filename": filename,
                "count": len(positions),
                "positions": positions[:5]
            })
    
    print(f"Found {len(result)} matches")
    return sorted(result, key=lambda x: x["count"], reverse=True)

# === PENCARIAN MULTIPLE KEYWORDS ===
def search_multiple_keywords(keywords, files, applicant_db, cv_mapping, algorithm='kmp', logic='and'):
    """Search multiple keywords using specified algorithm"""
    result = []
    keywords_lower = [kw.strip().lower() for kw in keywords if kw.strip()]
    
    algorithm_name = get_algorithm_name(algorithm)
    logic_desc = "ALL" if logic == 'and' else "ANY"
    
    print(f"Searching for {logic_desc} of {len(keywords_lower)} keywords using {algorithm_name}")
    print(f"Keywords: {', '.join(keywords_lower)}")
    print(f"Scanning {len(files)} CV files...")
    
    # Use Aho-Corasick for multiple keywords if selected
    if algorithm.lower() in ['ahocorasick', 'aho']:
        return search_keywords_aho_corasick(keywords_lower, files, applicant_db, cv_mapping, logic)
    
    # Use individual algorithm for each keyword
    for filename, text in files:
        keyword_results = {}
        total_matches = 0
        all_positions = []
        
        # Search each keyword in the current file
        for keyword in keywords_lower:
            positions = search_with_algorithm(text.lower(), keyword, algorithm)
            if positions:
                keyword_results[keyword] = {
                    'count': len(positions),
                    'positions': positions[:3]  # Store first 3 positions for context
                }
                total_matches += len(positions)
                all_positions.extend(positions)
        
        # Apply logic filter
        should_include = False
        if logic == 'and':
            # Include if ALL keywords are found
            should_include = (len(keyword_results) == len(keywords_lower))
        else:  # logic == 'or'
            # Include if ANY keyword is found
            should_include = (len(keyword_results) > 0)
        
        if should_include:
            name = get_applicant_name_by_cv(applicant_db, cv_mapping, filename.replace(".txt", ""))
            result.append({
                "name": name,
                "filename": filename,
                "total_count": total_matches,
                "keyword_details": keyword_results,
                "keywords_found": len(keyword_results),
                "all_positions": sorted(all_positions)[:10]  # First 10 positions for context
            })
    
    logic_desc = "ALL keywords" if logic == 'and' else "ANY of the keywords"
    print(f"Found {len(result)} CVs containing {logic_desc}")
    
    # Sort by number of different keywords found, then by total matches
    return sorted(result, key=lambda x: (x["keywords_found"], x["total_count"]), reverse=True)

# === PENCARIAN AHO-CORASICK (OPTIMIZED FOR MULTIPLE KEYWORDS) ===
def search_keywords_aho_corasick(keywords, files, applicant_db, cv_mapping, logic='and'):
    """Search keywords using Aho-Corasick algorithm (optimized for multiple patterns)"""
    result = []
    keywords_lower = [kw.strip().lower() for kw in keywords if kw.strip()]
    
    print(f"Using Aho-Corasick optimized search for {len(keywords_lower)} keywords")
    print(f"Keywords: {', '.join(keywords_lower)}")
    print(f"Scanning {len(files)} CV files...")
    
    for filename, text in files:
        text_lower = text.lower()
        
        # Use Aho-Corasick to find all patterns simultaneously
        matches = aho_corasick_search(text_lower, keywords_lower)
        
        if matches:
            # Group matches by pattern
            pattern_results = defaultdict(list)
            for pattern, start, end in matches:
                pattern_results[pattern].append((start, end))
            
            # Apply logic filter
            should_include = False
            if logic == 'and':
                # Include if ALL keywords are found
                should_include = (len(pattern_results) == len(keywords_lower))
            else:  # logic == 'or'
                # Include if ANY keyword is found
                should_include = (len(pattern_results) > 0)
            
            if should_include:
                # Calculate statistics
                total_matches = len(matches)
                keywords_found = len(pattern_results)
                
                name = get_applicant_name_by_cv(applicant_db, cv_mapping, filename.replace(".txt", ""))
                
                # Create detailed results for each keyword
                keyword_details = {}
                all_positions = []
                
                for keyword in keywords_lower:
                    if keyword in pattern_results:
                        positions = [start for start, end in pattern_results[keyword]]
                        keyword_details[keyword] = {
                            'count': len(positions),
                            'positions': positions[:3]  # Store first 3 positions for context
                        }
                        all_positions.extend(positions)
                
                result.append({
                    "name": name,
                    "filename": filename,
                    "total_count": total_matches,
                    "keyword_details": keyword_details,
                    "keywords_found": keywords_found,
                    "all_positions": sorted(all_positions)[:10],
                    "matches": matches[:20]  # Store first 20 matches for analysis
                })
    
    logic_desc = "ALL keywords" if logic == 'and' else "ANY of the keywords"
    print(f"Found {len(result)} CVs containing {logic_desc}")
    
    # Sort by number of different keywords found, then by total matches
    return sorted(result, key=lambda x: (x["keywords_found"], x["total_count"]), reverse=True)

# === TAMPILKAN CONTEXT ===
def show_context(text, positions, keyword, context_length=50):
    """Show context around found keywords"""
    contexts = []
    for pos in positions[:3]:  # Show max 3 contexts
        start = max(0, pos - context_length)
        end = min(len(text), pos + len(keyword) + context_length)
        context = text[start:end]
        
        # Highlight keyword (case insensitive)
        highlighted = context.lower().replace(keyword.lower(), keyword.upper())
        contexts.append(f"...{highlighted}...")
    
    return contexts

# === TAMPILKAN CONTEXT UNTUK MULTIPLE KEYWORDS ===
def show_context_multiple(text, keyword_details, context_length=50):
    """Show context around found keywords for multiple keywords"""
    for keyword, details in keyword_details.items():
        positions = details['positions']
        count = details['count']
        
        print(f"   '{keyword.upper()}': {count} kali ditemukan")
        
        # Use same logic as single keyword context
        contexts = show_context(text, positions, keyword, context_length)
        for i, ctx in enumerate(contexts, 1):
            print(f"     Context {i}: {ctx}")
        
        # Add separator between different keywords for readability
        if len(keyword_details) > 1:
            print("     " + "-" * 40)

# === PARSE KEYWORDS INPUT ===
def parse_keywords_input(input_text):
    """Parse keywords input - support comma separation and space separation"""
    # Try comma separation first
    if ',' in input_text:
        keywords = [kw.strip() for kw in input_text.split(',')]
    else:
        # Space separation for single words
        keywords = input_text.split()
    
    # Filter out empty keywords
    keywords = [kw for kw in keywords if kw.strip()]
    return keywords

# === GET ALGORITHM NAME ===
def get_algorithm_name(algorithm):
    """Get display name for algorithm"""
    if algorithm.lower() == 'kmp':
        return 'KMP'
    elif algorithm.lower() in ['boyer-moore', 'bm']:
        return 'Boyer-Moore'
    elif algorithm.lower() in ['ahocorasick', 'aho']:
        return 'Aho-Corasick'
    else:
        return algorithm.upper()

# === ALGORITHM SELECTION ===
def select_algorithm():
    """Let user select search algorithm"""
    print("\nPilih algoritma pencarian:")
    print("   1. KMP (Knuth-Morris-Pratt)")
    print("   2. Boyer-Moore")
    print("   3. Aho-Corasick (Optimal untuk multiple keywords)")
    
    while True:
        choice = input("Pilihan algoritma (1/2/3) [default: 1]: ").strip()
        
        if choice == '' or choice == '1':
            return 'kmp', 'KMP'
        elif choice == '2':
            return 'boyer-moore', 'Boyer-Moore'
        elif choice == '3':
            return 'ahocorasick', 'Aho-Corasick'
        else:
            print("Pilih 1 untuk KMP, 2 untuk Boyer-Moore, atau 3 untuk Aho-Corasick!")

# === PERFORMANCE COMPARISON ===
def compare_algorithms(keywords, files, algorithms=['kmp', 'boyer-moore', 'ahocorasick']):
    """Compare performance between algorithms"""
    print(f"\nMembandingkan performa algoritma untuk {'single keyword' if len(keywords) == 1 else 'multiple keywords'}...")
    
    results = {}
    
    for algo in algorithms:
        algo_name = get_algorithm_name(algo)
        print(f"Testing {algo_name}...")
        
        start_time = time.time()
        total_matches = 0
        
        if len(keywords) == 1:
            # Single keyword test
            keyword = keywords[0].lower()
            for filename, text in files:
                positions = search_with_algorithm(text.lower(), keyword, algo)
                total_matches += len(positions)
        else:
            # Multiple keywords test
            keywords_lower = [kw.lower() for kw in keywords]
            if algo.lower() in ['ahocorasick', 'aho']:
                # Use optimized Aho-Corasick for multiple keywords
                for filename, text in files:
                    matches = aho_corasick_search(text.lower(), keywords_lower)
                    total_matches += len(matches)
            else:
                # Use individual searches for other algorithms
                for filename, text in files:
                    for keyword in keywords_lower:
                        positions = search_with_algorithm(text.lower(), keyword, algo)
                        total_matches += len(positions)
        
        duration = time.time() - start_time
        results[algo_name] = {
            'duration': duration,
            'matches': total_matches
        }
        
        print(f"   {algo_name}: {duration:.4f}s ({int(duration * 1000)}ms)")
        print(f"   Matches: {total_matches}")
    
    # Show comparison
    print(f"\nPerformance Comparison:")
    sorted_results = sorted(results.items(), key=lambda x: x[1]['duration'])
    
    if len(sorted_results) > 1:
        fastest = sorted_results[0]
        print(f"🏆 Fastest: {fastest[0]} ({fastest[1]['duration']:.4f}s)")
        
        for i, (algo_name, data) in enumerate(sorted_results[1:], 1):
            speedup = data['duration'] / fastest[1]['duration']
            print(f"   {i+1}. {algo_name}: {speedup:.2f}x slower")
    
    # Special note for Aho-Corasick with multiple keywords
    if len(keywords) > 1 and 'Aho-Corasick' in results:
        print(f"\nNote: Aho-Corasick advantage increases with more keywords!")
    
    return results

# === MAIN ===
def main():
    print("Initializing CV Search System...")
    print(f"Current working directory: {os.getcwd()}")
    
    # Load database from SQL file
    applicant_db, cv_mapping = load_database_from_sql()
    
    print(f"\nDatabase Summary:")
    print(f"   Applicants loaded: {len(applicant_db)}")
    print(f"   CV mappings loaded: {len(cv_mapping)}")
    
    if not applicant_db and not cv_mapping:
        print("No database loaded! Check your init_db.sql file")
        return
    
    print("\n=== CV Keyword Search System ===")
    print("Features:")
    print("   - KMP, Boyer-Moore, ahocorasick algorithms")
    print("   - Single & Multiple keyword search")
    print("   - Performance comparison")
    print("   - AND/OR logic for multiple keywords")
    
    while True:
        print("\n" + "="*60)
        keyword_input = input("Masukkan keyword(s) (atau 'quit' untuk keluar): ").strip()
        
        if keyword_input.lower() == 'quit':
            break
        
        if not keyword_input:
            print("Keyword tidak boleh kosong!")
            continue

        # Parse keywords
        keywords = parse_keywords_input(keyword_input)
        
        if len(keywords) == 1:
            print(f"Mode: Single keyword search")
        else:
            print(f"Mode: Multiple keywords search ({len(keywords)} keywords)")
            print(f"Keywords: {', '.join(keywords)}")
        
        # Select algorithm
        algorithm, algorithm_name = select_algorithm()
        print(f"Selected algorithm: {algorithm_name}")
        
        # For multiple keywords, ask for search logic
        search_logic = 'and'  # default
        if len(keywords) > 1:
            while True:
                logic_choice = input("🔗 Search logic - (and/or)? [and]: ").lower().strip()
                if logic_choice in ['', 'and']:
                    search_logic = 'and'
                    print("Using AND logic: CV must contain ALL keywords")
                    break
                elif logic_choice == 'or':
                    search_logic = 'or'
                    print("Using OR logic: CV can contain ANY keyword")
                    break
                else:
                    print("Pilih 'and' atau 'or'!")

        # Ask for performance comparison (only for single keyword)
        compare_performance = False
        if len(keywords) == 1:
            comp_choice = input("Bandingkan performa dengan algoritma lain? (y/n): ").lower().strip()
            compare_performance = (comp_choice == 'y')

        # Input untuk jumlah hasil yang ditampilkan
        while True:
            try:
                max_results_input = input("Berapa hasil teratas yang ingin ditampilkan? (default: 10, 'all' untuk semua): ").strip()
                
                if max_results_input.lower() == 'all':
                    max_results = None
                    break
                elif max_results_input == '':
                    max_results = 10
                    break
                else:
                    max_results = int(max_results_input)
                    if max_results <= 0:
                        print("Masukkan angka positif!")
                        continue
                    break
            except ValueError:
                print("Masukkan angka yang valid atau 'all'!")
                continue

        print(f"\nMencari dengan {algorithm_name}...")
        start = time.time()

        # Load files
        files = load_pattern_files()
        if not files:
            print("Tidak ada file pattern matching yang ditemukan!")
            continue

        # Perform search
        if len(keywords) == 1:
            # Single keyword search
            results = search_keyword(keywords[0], files, applicant_db, cv_mapping, algorithm)
        else:
            # Multiple keywords search
            results = search_multiple_keywords(keywords, files, applicant_db, cv_mapping, algorithm, search_logic)

        duration = time.time() - start
        print(f"\n{algorithm_name} Search completed in {duration:.3f}s ({int(duration * 1000)}ms)")

        # Performance comparison if requested
        if compare_performance and len(keywords) == 1:
            other_algorithm = 'boyer-moore' if algorithm == 'kmp' else 'kmp'
            compare_algorithms(keywords[0], files, algorithm, other_algorithm)

        # Display results
        if results:
            # Determine how many results to show
            if max_results is None:
                results_to_show = results
                print(f"\n=== Hasil Pencarian: Menampilkan SEMUA {len(results)} kandidat ===")
            else:
                results_to_show = results[:max_results]
                print(f"\n=== Hasil Pencarian: Menampilkan TOP {len(results_to_show)} dari {len(results)} kandidat ===")
            
            # Ask if user wants to see context for all results
            show_all_context = False
            if len(results_to_show) > 3:
                context_choice = input("\nTampilkan konteks untuk semua hasil? (y/n/ask): ").lower().strip()
                if context_choice == 'y':
                    show_all_context = True
                elif context_choice == 'ask':
                    show_all_context = 'ask'
                else:
                    show_all_context = False
            
            for idx, res in enumerate(results_to_show, 1):
                print(f"\n{idx}. {res['name']}")
                print(f"   File: {res['filename']}")
                
                # Display match information based on search type
                if len(keywords) == 1:
                    print(f"   Kemunculan: {res['count']} kali")
                else:
                    print(f"   Total kemunculan: {res['total_count']} kali")
                    print(f"   Keywords ditemukan: {res['keywords_found']}/{len(keywords)}")
                    
                    # Show breakdown by keyword
                    for keyword, details in res['keyword_details'].items():
                        print(f"     • '{keyword}': {details['count']} kali")
                
                # Determine whether to show context
                should_show_context = False
                
                if show_all_context is True:
                    should_show_context = True
                elif show_all_context == 'ask':
                    show_detail = input("   Tampilkan konteks untuk kandidat ini? (y/n): ").lower().strip()
                    should_show_context = (show_detail == 'y')
                elif idx <= 3:
                    show_detail = input("   Tampilkan konteks? (y/n): ").lower().strip()
                    should_show_context = (show_detail == 'y')
                
                # Show context if requested
                if should_show_context:
                    for fname, text in files:
                        if fname == res['filename']:
                            if len(keywords) == 1:
                                # Single keyword context
                                contexts = show_context(text, res['positions'], keywords[0].lower())
                                for i, ctx in enumerate(contexts, 1):
                                    print(f"   Context {i}: {ctx}")
                            else:
                                # Multiple keywords context
                                print("   Context untuk setiap keyword:")
                                show_context_multiple(text, res['keyword_details'])
                            break
                    
                    # Add separator for readability
                    if show_all_context is True and idx < len(results_to_show):
                        print("   " + "-"*60)
            
            # Show summary if not all results were displayed
            if max_results is not None and len(results) > max_results:
                remaining = len(results) - max_results
                print(f"\nAda {remaining} kandidat lainnya yang tidak ditampilkan.")
                show_more = input("Ingin melihat semua hasil? (y/n): ").lower().strip()
                if show_more == 'y':
                    print(f"\n=== SEMUA Hasil Pencarian ({len(results)} kandidat) ===")
                    for idx, res in enumerate(results, 1):
                        if len(keywords) == 1:
                            print(f"{idx}. {res['name']} - {res['count']} kali ({res['filename']})")
                        else:
                            print(f"{idx}. {res['name']} - {res['total_count']} total, {res['keywords_found']}/{len(keywords)} keywords ({res['filename']})")
                        
        else:
            if len(keywords) == 1:
                print("Tidak ditemukan hasil exact match.")
            else:
                print(f"Tidak ditemukan CV yang mengandung {'semua' if search_logic == 'and' else 'salah satu dari'} keyword yang dicari.")
            print("💡 Tips: Coba kata kunci yang lebih umum atau periksa ejaan")

    print("\nTerima kasih telah menggunakan CV Search System!")

if __name__ == "__main__":
    main()