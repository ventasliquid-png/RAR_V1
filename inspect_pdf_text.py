import sys
from pypdf import PdfReader

try:
    reader = PdfReader("factura_muestra.pdf")
    print(f"Number of Pages: {len(reader.pages)}")
    for i, page in enumerate(reader.pages):
        print(f"--- Page {i+1} ---")
        print(page.extract_text())
except Exception as e:
    print(f"Error reading PDF: {e}")
