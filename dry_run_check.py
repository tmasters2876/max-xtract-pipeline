import os
import csv
import json
from supabase import create_client
from dotenv import load_dotenv

# Load env
load_dotenv()

# Supabase
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
supabase = create_client(url, key)

# Load correct links
with open("document_links.json", encoding="utf-8") as f:
    doc_links = json.load(f)

# Load local clauses rows
with open("clauses_rows.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("\n🔍 Starting dry run comparison...")

changes = []
unchanged = []

for row in rows:
    clause_id = row["clause_id"]
    document = row["document"]
    new_link = doc_links.get(document, "")

    # Get current link in Supabase
    response = supabase.table("clauses").select("link").eq("clause_id", clause_id).single().execute()
    current_link = response.data["link"] if response.data else None

    if current_link != new_link:
        changes.append({
            "clause_id": clause_id,
            "document": document,
            "current_link": current_link,
            "new_link": new_link
        })
    else:
        unchanged.append(clause_id)

print(f"\n✅ Changes Needed: {len(changes)}")
print(f"✅ Unchanged: {len(unchanged)}\n")

for item in changes:
    print(f"- {item['clause_id']}:")
    print(f"   Document: {item['document']}")
    print(f"   Current: {item['current_link']}")
    print(f"   New:     {item['new_link']}\n")

print("🟢 Dry run complete. No writes done.")
