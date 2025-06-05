# batch_debug_retry.py
import openai
import json
import os
from dotenv import load_dotenv
from batch_gpt_parse import parse_page_with_gpt

load_dotenv()

# === CONFIG ===
PAGES_TO_RETRY = [12, 13, 14, 15]  # The pages that previously returned valid clause matches

# === Load pages.json ===
with open("pages.json", "r") as f:
    pages = json.load(f)

# === Filter for specific pages ===
target_pages = [p for p in pages if p["page"] in PAGES_TO_RETRY]

if not target_pages:
    print("❌ No matching pages found for retry.")
    exit()

# === Retry GPT clause extraction ===
for page in target_pages:
    doc = page["document"]
    page_number = page["page"]
    text = page["text"]

    print(f"\n🔁 Retesting GPT extraction for {doc} — Page {page_number}...\n")
    clauses = parse_page_with_gpt(text, page_number, doc)

    if not clauses:
        print(f"⚠️ No clauses returned on page {page_number}")
    else:
        print(f"✅ {len(clauses)} clause(s) extracted from page {page_number}:")
        print(json.dumps(clauses, indent=2))
