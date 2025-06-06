import sys
import fitz  
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QScrollArea
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import os

class PDFViewer(QMainWindow):
    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.doc = None
        self.setWindowTitle("PyMuPDF PDF Viewer")
        self.setGeometry(100, 100, 800, 900) 
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop) 
        self.scroll_area.setWidget(self.content_widget)

        self.load_pdf()

    def load_pdf(self):
        if not os.path.exists(self.pdf_path):
            print(f"Error: File tidak ditemukan di '{self.pdf_path}'")
            error_label = QLabel(f"Error: File tidak ditemukan di '{self.pdf_path}'")
            error_label.setStyleSheet("color: red;")
            self.content_layout.addWidget(error_label)
            return

        try:
            self.doc = fitz.open(self.pdf_path)
            print(f"Memuat {self.doc.page_count} halaman dari '{self.pdf_path}'")

            for page_num in range(self.doc.page_count):
                page = self.doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 

 
                if pix.alpha:
                    img_format = QImage.Format_RGBA8888
                elif pix.n == 1:
                    img_format = QImage.Format_Grayscale8
                else:
                    img_format = QImage.Format_RGB888

                qimage = QImage(
                    pix.samples,
                    pix.width,
                    pix.height,
                    pix.stride, 
                    img_format
                )

                if img_format == QImage.Format_RGB888:
                    qimage = qimage.rgbSwapped()

                pixmap = QPixmap.fromImage(qimage)

                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignCenter) 
                self.content_layout.addWidget(label)

                if page_num < self.doc.page_count - 1:
                    self.content_layout.addSpacing(20)

        except Exception as e:
            print(f"Terjadi kesalahan saat memuat atau merender PDF: {e}")
            error_label = QLabel(f"Error: Terjadi kesalahan saat memuat PDF: {e}")
            error_label.setStyleSheet("color: red;")
            self.content_layout.addWidget(error_label)
        finally:
            if self.doc:
                self.doc.close() 

def show_cv_pymupdf_gui(pdf_path):
    app = QApplication(sys.argv)
    viewer = PDFViewer(pdf_path)
    viewer.show()
    sys.exit(app.exec_())

