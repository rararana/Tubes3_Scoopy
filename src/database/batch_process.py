import os
from .extract_and_store import process_file

PDF_DIR = "data/"

def batch_process(role="Default Role"):
    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR, file)
            process_file(pdf_path, role)

# if __name__ == "__main__":
#     batch_process(role="Kitchen Staff")
