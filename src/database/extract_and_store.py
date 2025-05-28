import fitz
import re
import os
import json
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting PDF {pdf_path}: {e}")
        return ""

def save_pattern_text(text, output_path):
    """Save cleaned text for pattern matching"""
    cleaned = " ".join(text.replace("\n", " ").lower().split())
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

def save_regex_text(text, output_path):
    """Save original text for regex processing"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def extract_sections_flexible(text):
    """Extract sections from CV text"""
    headings = [
        "Skills", "Summary", "Highlights", "Accomplishments", "Experience", "Education",
        "Certifications", "Projects", "Technical Skills", "Languages", "Awards"
    ]
    pattern = rf"(?P<header>^({'|'.join(map(re.escape, headings))})\s*$)"
    matches = list(re.finditer(pattern, text, flags=re.MULTILINE | re.IGNORECASE))
    result = {}
    for i, match in enumerate(matches):
        header = match.group("header").strip().title()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        result[header] = text[start:end].strip()
    return result

def process_single_file(pdf_path, role):
    """Process single PDF file"""
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        print(f"⚠️  No text extracted from {pdf_path}")
        return False
    
    # Create output directories
    os.makedirs("data/pattern_matching", exist_ok=True)
    os.makedirs("data/regex_data", exist_ok=True)
    os.makedirs("data/structured_info", exist_ok=True)
    
    # Save pattern matching text (cleaned)
    save_pattern_text(text, f"data/pattern_matching/{filename}.txt")
    
    # Save regex text (original)
    save_regex_text(text, f"data/regex_data/{filename}.txt")
    
    # Extract sections and save as JSON
    sections = extract_sections_flexible(text)
    structured_info = {
        "filename": filename,
        "role": role,
        "sections": sections,
        "text_length": len(text),
        "processed_at": datetime.now().isoformat()
    }
    
    with open(f"data/structured_info/{filename}.json", "w", encoding="utf-8") as jf:
        json.dump(structured_info, jf, ensure_ascii=False, indent=2)
    
    print(f"✓ Processed {filename} ({role}) - {len(text)} characters")
    return True

def process_all_files():
    """Process all PDF files in all role folders"""
    base_data_dir = "data"
    
    # Define all roles (folders)
    roles = [
        'ACCOUNTANT', 'ADVOCATE', 'AGRICULTURE', 'APPAREL', 'ARTS', 'AUTOMOBILE',
        'AVIATION', 'BANKING', 'BPO', 'BUSINESS-DEVELOPMENT', 'CHEF', 'CONSTRUCTION',
        'CONSULTANT', 'DESIGNER', 'DIGITAL-MEDIA', 'ENGINEERING', 'FINANCE',
        'FITNESS', 'HEALTHCARE', 'HR', 'INFORMATION-TECHNOLOGY', 'PUBLIC-RELATIONS',
        'SALES', 'TEACHER'
    ]
    
    total_processed = 0
    total_files = 0
    
    for role in roles:
        role_dir = os.path.join(base_data_dir, role)
        
        if not os.path.exists(role_dir):
            print(f"⚠️  Directory not found: {role_dir}")
            continue
        
        # Get all PDF files in the role directory
        pdf_files = [f for f in os.listdir(role_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in {role_dir}")
            continue
        
        print(f"\n📁 Processing {role} ({len(pdf_files)} files):")
        
        role_processed = 0
        for pdf_file in sorted(pdf_files):
            pdf_path = os.path.join(role_dir, pdf_file)
            total_files += 1
            
            if process_single_file(pdf_path, role):
                role_processed += 1
                total_processed += 1
        
        print(f"   ✅ {role}: {role_processed}/{len(pdf_files)} files processed")
    
    print(f"\n🎉 SUMMARY:")
    print(f"   Total files found: {total_files}")
    print(f"   Successfully processed: {total_processed}")
    print(f"   Failed: {total_files - total_processed}")
    
    # Display output structure
    print(f"\n📂 Output directories created:")
    print(f"   - data/pattern_matching/ (cleaned text for pattern matching)")
    print(f"   - data/regex_data/ (original text for regex)")
    print(f"   - data/structured_info/ (JSON with extracted sections)")

def process_specific_role(role_name):
    """Process files from specific role only"""
    base_data_dir = "data"
    role_dir = os.path.join(base_data_dir, role_name.upper())
    
    if not os.path.exists(role_dir):
        print(f"⚠️  Directory not found: {role_dir}")
        return
    
    pdf_files = [f for f in os.listdir(role_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {role_dir}")
        return
    
    print(f"📁 Processing {role_name} ({len(pdf_files)} files):")
    
    processed = 0
    for pdf_file in sorted(pdf_files):
        pdf_path = os.path.join(role_dir, pdf_file)
        if process_single_file(pdf_path, role_name):
            processed += 1
    
    print(f"✅ {role_name}: {processed}/{len(pdf_files)} files processed")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Process specific role if provided as argument
        role_name = sys.argv[1]
        process_specific_role(role_name)
    else:
        # Process all files
        print("🚀 Starting extraction for all PDF files...")
        process_all_files()