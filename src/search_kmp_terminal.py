import os
import time
import json
import sys
import re
from algorithms.kmp import kmp_search

# === LOAD DATABASE FROM SQL FILE ===
def load_database_from_sql():
    """Load applicant data from init_db.sql file"""
    applicant_db = {}
    cv_mapping = {}
    
    print("🔍 Starting database load...")
    
    # Coba berbagai lokasi file SQL
    possible_sql_paths = [
        "src/database/init_db.sql",
        "database/init_db.sql", 
        "../database/init_db.sql",
        "../../src/database/init_db.sql"
    ]
    
    print("📍 Checking SQL file locations:")
    for path in possible_sql_paths:
        exists = os.path.exists(path)
        print(f"   {path}: {'✅' if exists else '❌'}")
    
    sql_file = None
    for path in possible_sql_paths:
        if os.path.exists(path):
            sql_file = path
            break
    
    if not sql_file:
        print("⚠️  File init_db.sql tidak ditemukan!")
        return {}, {}
    
    try:
        print(f"📄 Reading SQL file: {sql_file}")
        with open(sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📏 SQL file size: {len(content)} characters")
        
        # Extract ApplicantProfile data
        print("🔍 Looking for ApplicantProfile data...")
        profile_pattern = r"INSERT INTO ApplicantProfile.*?VALUES\s*(.*?)(?=INSERT|$)"
        profile_match = re.search(profile_pattern, content, re.DOTALL)
        
        if profile_match:
            values_text = profile_match.group(1)
            print(f"📝 ApplicantProfile values text length: {len(values_text)}")
            
            # Parse each row
            row_pattern = r"\(\s*(\d+),\s*'([^']+)',\s*'([^']+)',\s*'[^']*',\s*'[^']*'\)"
            rows = re.findall(row_pattern, values_text)
            
            print(f"🔍 Found {len(rows)} applicant profiles")
            
            for applicant_id, first_name, last_name in rows:
                applicant_db[int(applicant_id)] = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': f"{first_name} {last_name}"
                }
                
            # Print first few entries
            if applicant_db:
                print("📝 Sample applicants loaded:")
                for i, (aid, data) in enumerate(list(applicant_db.items())[:3]):
                    print(f"   ID {aid}: {data['full_name']}")
        else:
            print("❌ No ApplicantProfile INSERT statement found")
        
        # Extract ApplicationDetail data
        print("🔍 Looking for ApplicationDetail data...")
        detail_pattern = r"INSERT INTO ApplicationDetail.*?VALUES\s*(.*?)(?=INSERT|$)"
        detail_matches = re.findall(detail_pattern, content, re.DOTALL)
        
        print(f"🔍 Found {len(detail_matches)} ApplicationDetail blocks")
        
        total_mappings = 0
        missing_ids = set()
        
        for i, match in enumerate(detail_matches):
            print(f"📝 Processing block {i+1}, length: {len(match)}")
            
            # Parse each row
            row_pattern = r"\(\s*(\d+),\s*'([^']+)',\s*'[^']*?/([^/]+?)\.pdf'\)"
            rows = re.findall(row_pattern, match)
            
            print(f"   Found {len(rows)} rows in this block")
            
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
        
        print(f"✅ Total CV mappings: {total_mappings}")
        print(f"⚠️  Missing applicant IDs: {len(missing_ids)}")
        
        # Create mock entries for missing IDs
        if missing_ids:
            print("🔧 Creating mock entries for missing applicant IDs...")
            
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
            
            print(f"✅ Created {len(missing_ids)} mock applicant entries")
        
        # Print sample CV mappings
        if cv_mapping:
            print("📝 Sample CV mappings:")
            for i, (filename, data) in enumerate(list(cv_mapping.items())[:5]):
                aid = data['applicant_id']
                name = applicant_db.get(aid, {}).get('full_name', f'ID_{aid}')
                print(f"   {filename}: {name} (ID {aid}, {data['role']})")
        
        return applicant_db, cv_mapping
        
    except Exception as e:
        print(f"❌ Error reading SQL file: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

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
            # This should not happen anymore with mock data
            return f"Missing_ID_{applicant_id} ({role})"
    
    return f"Unknown ({filename})"

# ... rest of the code remains the same ...

# === LOAD FILE-FILE PATTERN MATCHING ===
def load_pattern_files():
    """Load all pattern matching text files"""
    result = []
    
    print("🔍 Looking for pattern matching files...")
    
    # Coba berbagai kemungkinan lokasi folder pattern_matching
    possible_folders = [
        "data/pattern_matching",
        "../data/pattern_matching",
        "../../data/pattern_matching",
    ]
    
    print("📍 Checking pattern_matching folders:")
    for path in possible_folders:
        exists = os.path.exists(path)
        print(f"   {path}: {'✅' if exists else '❌'}")
    
    folder_path = None
    for path in possible_folders:
        if os.path.exists(path):
            folder_path = path
            break
    
    if not folder_path:
        print("❌ Folder pattern_matching tidak ditemukan!")
        return result
    
    print(f"📁 Using folder: {os.path.abspath(folder_path)}")
    
    # List all files in folder
    all_files = os.listdir(folder_path)
    txt_files = [f for f in all_files if f.endswith('.txt')]
    
    print(f"📄 Found {len(all_files)} total files, {len(txt_files)} .txt files")
    
    for filename in txt_files[:5]:  # Show first 5 files
        print(f"   📝 {filename}")
    
    if len(txt_files) > 5:
        print(f"   ... and {len(txt_files) - 5} more files")
    
    for filename in txt_files:
        path = os.path.join(folder_path, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                result.append((filename, text))
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
    
    print(f"✅ Loaded {len(result)} pattern files")
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

# === PENCARIAN KMP ===
def search_keyword_kmp(keyword, files, applicant_db, cv_mapping):
    """Search keyword using KMP algorithm"""
    result = []
    keyword_lower = keyword.lower()
    
    print(f"🔍 Searching for '{keyword_lower}' in {len(files)} files...")
    
    for filename, text in files:
        positions = kmp_search(text, keyword_lower)
        if positions:
            name = get_applicant_name_by_cv(applicant_db, cv_mapping, filename.replace(".txt", ""))
            result.append({
                "name": name,
                "filename": filename,
                "count": len(positions),
                "positions": positions[:5]
            })
    
    print(f"🎯 Found {len(result)} matches")
    return sorted(result, key=lambda x: x["count"], reverse=True)

# === TAMPILKAN CONTEXT ===
def show_context(text, positions, keyword, context_length=50):
    """Show context around found keywords"""
    contexts = []
    for pos in positions[:3]:
        start = max(0, pos - context_length)
        end = min(len(text), pos + len(keyword) + context_length)
        context = text[start:end]
        highlighted = context.replace(keyword.lower(), keyword.upper())
        contexts.append(f"...{highlighted}...")
    return contexts

# === MAIN ===
def main():
    print("🚀 Initializing CV Search System...")
    print(f"📍 Current working directory: {os.getcwd()}")
    
    # Load database from SQL file
    applicant_db, cv_mapping = load_database_from_sql()
    
    print(f"\n📊 Database Summary:")
    print(f"   Applicants loaded: {len(applicant_db)}")
    print(f"   CV mappings loaded: {len(cv_mapping)}")
    
    if not applicant_db and not cv_mapping:
        print("❌ No database loaded! Check your init_db.sql file")
        return
    
    print("\n=== KMP CV Keyword Search ===")
    print("💡 Tips: Gunakan keyword seperti 'python', 'java', 'management', 'experience'")
    
    while True:
        print("\n" + "="*50)
        keyword = input("🔍 Masukkan keyword (atau 'quit' untuk keluar): ").strip()
        
        if keyword.lower() == 'quit':
            break
        
        if not keyword:
            print("⚠️  Keyword tidak boleh kosong!")
            continue

        # Input untuk jumlah hasil yang ditampilkan
        while True:
            try:
                max_results_input = input("📊 Berapa hasil teratas yang ingin ditampilkan? (default: 10, 'all' untuk semua): ").strip()
                
                if max_results_input.lower() == 'all':
                    max_results = None  # Show all results
                    break
                elif max_results_input == '':
                    max_results = 10  # Default
                    break
                else:
                    max_results = int(max_results_input)
                    if max_results <= 0:
                        print("⚠️  Masukkan angka positif!")
                        continue
                    break
            except ValueError:
                print("⚠️  Masukkan angka yang valid atau 'all'!")
                continue

        print(f"\n🔍 Mencari dengan KMP: '{keyword}'...")
        start = time.time()

        # Load files
        files = load_pattern_files()
        if not files:
            print("❌ Tidak ada file pattern matching yang ditemukan!")
            continue

        # Search using KMP
        results = search_keyword_kmp(keyword, files, applicant_db, cv_mapping)
        duration = time.time() - start

        print(f"\n✅ KMP Search completed in {duration:.3f}s ({int(duration * 1000)}ms)")

        if results:
            # Determine how many results to show
            if max_results is None:
                results_to_show = results
                print(f"\n=== 🎯 Hasil Pencarian: Menampilkan SEMUA {len(results)} kandidat ===")
            else:
                results_to_show = results[:max_results]
                print(f"\n=== 🎯 Hasil Pencarian: Menampilkan TOP {len(results_to_show)} dari {len(results)} kandidat ===")
            
            # Ask if user wants to see context for all results
            show_all_context = False
            if len(results_to_show) > 3:
                context_choice = input("\n👀 Tampilkan konteks untuk semua hasil? (y/n/ask): ").lower().strip()
                if context_choice == 'y':
                    show_all_context = True
                elif context_choice == 'ask':
                    show_all_context = 'ask'
                else:
                    show_all_context = False
            
            for idx, res in enumerate(results_to_show, 1):
                print(f"\n{idx}. {res['name']}")
                print(f"   📄 File: {res['filename']}")
                print(f"   🔢 Kemunculan: {res['count']} kali")
                
                # Determine whether to show context
                should_show_context = False
                
                if show_all_context is True:
                    should_show_context = True
                elif show_all_context == 'ask':
                    show_detail = input("   👀 Tampilkan konteks untuk kandidat ini? (y/n): ").lower().strip()
                    should_show_context = (show_detail == 'y')
                elif idx <= 3:  # Default behavior for top 3
                    show_detail = input("   👀 Tampilkan konteks? (y/n): ").lower().strip()
                    should_show_context = (show_detail == 'y')
                
                # Show context if requested
                if should_show_context:
                    for fname, text in files:
                        if fname == res['filename']:
                            contexts = show_context(text, res['positions'], keyword.lower())
                            for i, ctx in enumerate(contexts, 1):
                                print(f"   📝 Context {i}: {ctx}")
                            break
                    
                    # Add separator for readability when showing multiple contexts
                    if show_all_context is True and idx < len(results_to_show):
                        print("   " + "-"*60)
            
            # Show summary if not all results were displayed
            if max_results is not None and len(results) > max_results:
                remaining = len(results) - max_results
                print(f"\n💡 Ada {remaining} kandidat lainnya yang tidak ditampilkan.")
                show_more = input("📋 Ingin melihat semua hasil? (y/n): ").lower().strip()
                if show_more == 'y':
                    print(f"\n=== 📋 SEMUA Hasil Pencarian ({len(results)} kandidat) ===")
                    for idx, res in enumerate(results, 1):
                        print(f"{idx}. {res['name']} - {res['count']} kali ({res['filename']})")
                        
        else:
            print("❌ Tidak ditemukan hasil exact match.")
            print("💡 Tips: Coba kata kunci yang lebih umum atau periksa ejaan")

    print("\n👋 Terima kasih telah menggunakan CV Search System!")

if __name__ == "__main__":
    main()