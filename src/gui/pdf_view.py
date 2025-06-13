import sys
import fitz  
import os
import threading
import subprocess

def show_cv_pymupdf_gui(pdf_path):
    """Show PDF using available methods"""
    if not os.path.exists(pdf_path):
        print(f"Error: File tidak ditemukan di '{pdf_path}'")
        return
    
    print(f"Attempting to open PDF: {pdf_path}")
    
    # Method 1: Try system default first
    try:
        if sys.platform.startswith('linux'):
            result = subprocess.run(['xdg-open', pdf_path], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("PDF opened with system default")
                return
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', pdf_path], check=True)
            return
        elif sys.platform == 'win32':  # Windows
            os.startfile(pdf_path)
            return
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print("System default failed, trying alternatives...")
    
    # Method 2: Try specific PDF viewers
    success = try_alternative_viewers(pdf_path)
    
    # Method 3: If all fails, show text preview
    if not success:
        print("All PDF viewers failed, showing text preview...")
        show_pdf_info(pdf_path)

def try_alternative_viewers(pdf_path):
    """Try alternative PDF viewers"""
    # Ordered list of viewers to try (most likely to work first)
    viewers = [
        'evince',           # GNOME PDF viewer
        'okular',           # KDE PDF viewer  
        'firefox-esr',      # Firefox ESR
        'firefox',          # Regular Firefox
        'chromium-browser', # Chromium
        'google-chrome',    # Chrome
        'atril',           # MATE PDF viewer
        'qpdfview',        # Qt PDF viewer
        'mupdf',           # Lightweight PDF viewer
        'zathura'          # Minimalist PDF viewer
    ]
    
    for viewer in viewers:
        try:
            # Check if viewer exists first
            check_result = subprocess.run(['which', viewer], 
                                        capture_output=True, text=True)
            if check_result.returncode != 0:
                continue  # Viewer not installed
            
            # Try to open PDF
            result = subprocess.run([viewer, pdf_path], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                print(f"PDF opened successfully with {viewer}")
                return True
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print("All PDF viewers failed")
    return False

def show_pdf_info(pdf_path):
    """Show PDF information and text preview"""
    try:
        doc = fitz.open(pdf_path)
        print(f"\n" + "="*50)
        print(f"📄 PDF PREVIEW: {os.path.basename(pdf_path)}")
        print("="*50)
        print(f"📍 Location: {pdf_path}")
        print(f"📊 Pages: {doc.page_count}")
        print(f"📝 Title: {doc.metadata.get('title', 'N/A')}")
        print(f"👤 Author: {doc.metadata.get('author', 'N/A')}")
        
        # Show first page text preview
        if doc.page_count > 0:
            page = doc.load_page(0)
            text = page.get_text()
            print(f"\n📖 FIRST PAGE PREVIEW:")
            print("-" * 30)
            preview_text = text[:800] if len(text) > 800 else text
            print(preview_text)
            if len(text) > 800:
                print("...")
                print(f"\n[Total text length: {len(text)} characters]")
        
        doc.close()
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")

def show_cv_threaded(pdf_path):
    """Show CV in separate thread to avoid GUI blocking"""
    thread = threading.Thread(target=show_cv_pymupdf_gui, args=(pdf_path,))
    thread.daemon = True
    thread.start()

# Additional helper function for GUI
def check_pdf_viewers_available():
    """Check which PDF viewers are available on the system"""
    viewers = ['evince', 'okular', 'firefox-esr', 'firefox', 'chromium-browser']
    available = []
    
    for viewer in viewers:
        try:
            result = subprocess.run(['which', viewer], capture_output=True, text=True)
            if result.returncode == 0:
                available.append(viewer)
        except FileNotFoundError:
            continue
    
    return available