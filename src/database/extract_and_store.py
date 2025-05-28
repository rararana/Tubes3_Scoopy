import fitz
import re
import os
import json
from datetime import datetime
from db_connector import insert_applicant, insert_application_detail

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

def save_pattern_text(text, output_path):
    cleaned = " ".join(text.replace("\n", " ").lower().split())
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

def save_regex_text(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def extract_sections_flexible(text):
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

def extract_info_full(text):
    lines = text.strip().splitlines()
    name_line = next((line.strip() for line in lines if line.strip()), "Unknown")
    first_name = name_line.split()[0]
    last_name = name_line.split()[-1] if len(name_line.split()) > 1 else ""
    phone_match = re.search(r"(\+?\d[\d\s\-]{7,})", text)
    phone = phone_match.group(1).strip() if phone_match else "0000000000"
    dob = None
    address = "Unknown"

    sections = extract_sections_flexible(text)

    return {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob,
        "address": address,
        "phone": phone,
        "summary": sections.get("Summary", ""),
        "highlights": sections.get("Highlights", ""),
        "accomplishments": sections.get("Accomplishments", ""),
        "experience": sections.get("Experience", ""),
        "education": sections.get("Education", ""),
        "skills": sections.get("Skills", "")
    }

def process_file(pdf_path, role):
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    text = extract_text_from_pdf(pdf_path)
    info = extract_info_full(text)

    os.makedirs("data/pattern_matching", exist_ok=True)
    save_pattern_text(text, f"data/pattern_matching/{filename}.txt")

    os.makedirs("data/regex_data", exist_ok=True)
    save_regex_text(text, f"data/regex_data/{filename}.txt")

    os.makedirs("data/structured_info", exist_ok=True)
    with open(f"data/structured_info/{filename}.json", "w", encoding="utf-8") as jf:
        json.dump(info, jf, ensure_ascii=False, indent=2)

    applicant_id = insert_applicant(
        info["first_name"], info["last_name"],
        info["date_of_birth"], info["address"], info["phone"]
    )
    insert_application_detail(applicant_id, role, pdf_path)

    print(f"✓ Inserted {info['first_name']} {info['last_name']} with ID {applicant_id}")
    return info


if __name__ == "__main__":
    process_file("data/27573855.pdf", "Accountant")
