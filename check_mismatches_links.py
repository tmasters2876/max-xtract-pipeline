import csv
import json

# Load sources
with open("clauses_rows.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

with open("document_links.json", encoding="utf-8") as f:
    doc_links = json.load(f)

missing = set()
for row in rows:
    doc_name = row["document"]
    if doc_name not in doc_links:
        missing.add(doc_name)

print("MISSING DOCUMENT LINKS:")
for doc in sorted(missing):
    print(f"- {doc}")

print(f"✅ {len(missing)} missing document link(s).")
