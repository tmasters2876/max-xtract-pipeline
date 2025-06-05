import os
import json
import pdfplumber

INPUT_FOLDER = "./docs"  # ✅ Safer test run
OUTPUT_FILE = "pages.json"

def extract_pages():
    output = []

    for filename in os.listdir(INPUT_FOLDER):
        if not filename.endswith(".pdf"):
            continue

        file_path = os.path.join(INPUT_FOLDER, filename)
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                output.append({
                    "document": filename,
                    "page": i + 1,
                    "text": text.strip()
                })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted {len(output)} pages into {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_pages()
