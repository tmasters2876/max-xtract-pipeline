import os
import json
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Load trusted clean links
with open("document_links.json", "r", encoding="utf-8") as f:
    document_links = json.load(f)

# Fetch all clauses from Supabase
response = supabase.table("clauses").select("*").execute()
clauses = response.data

repaired = 0
skipped = 0
total = len(clauses)

for clause in clauses:
    clause_id = clause.get("clause_id")
    doc = clause.get("document")
    current_link = clause.get("link")
    correct_link = document_links.get(doc)

    if not clause_id or not doc or not correct_link:
        skipped += 1
        continue

    if current_link != correct_link:
        supabase.table("clauses").update({"link": correct_link}).eq("clause_id", clause_id).execute()
        repaired += 1
    else:
        skipped += 1

print(f"✅ Link repair complete.")
print(f"🔧 Total clauses checked: {total}")
print(f"🔄 Repaired: {repaired}")
print(f"⏭️ Skipped (already correct or missing doc): {skipped}")
