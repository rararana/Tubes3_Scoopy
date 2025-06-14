import os
from typing import List, Tuple

def load_cv_text_files() -> List[Tuple[str, str]]:
    """
    Memuat semua file .txt dari direktori pattern_matching.
    """
    pattern_files = []
    folder_path = "data/pattern_matching" if os.path.exists("data/pattern_matching") else "pattern_matching"
    
    if not os.path.exists(folder_path):
        print("Pattern matching folder not found")
        return []
        
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                    pattern_files.append((filename, f.read()))
        print(f"Loaded {len(pattern_files)} pattern files")
        return pattern_files
    except Exception as e:
        print(f"Error loading data: {e}")
        return []
    
def parse_cv_text_file(filename: str) -> dict:
    """
    Mem-parsing file teks CV menjadi beberapa bagian: Experience, Education, Skills.
    """
    parsed_data = {"Experience": "", "Education": "", "Skills": ""}
    filepath = os.path.join("data", "regex_data", filename)
    
    if not os.path.exists(filepath):
        print(f"File not found for parsing: {filepath}")
        return parsed_data
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        current_section = None
        for line in content.split('\n'):
            line_stripped = line.strip().lower().replace(":", "")

            if any(keyword in line_stripped for keyword in ["experience", "work history", "employment"]) and len(line_stripped.split()) < 4:
                current_section = "Experience"
            elif any(keyword in line_stripped for keyword in ["education", "training"]) and len(line_stripped.split()) < 4:
                current_section = "Education"
            elif "skills" in line_stripped and len(line_stripped.split()) < 4:
                current_section = "Skills"
            elif current_section:
                parsed_data[current_section] += line + "\n"

    except Exception as e:
        print(f"Error parsing {filename}: {e}")
    
    for key in parsed_data:
        parsed_data[key] = parsed_data[key].strip()

    return parsed_data