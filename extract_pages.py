import pdfplumber

def extract_pages_from_pdf(pdf_path, document_name):
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages.append({
                        "document": document_name,
                        "page": i + 1,
                        "text": text.strip()
                    })
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
    return pages
