import os, json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Config
DRY_RUN = False
VERBOSE = False

# Load precedence level map from external JSON
with open("precedence_map_extension.json", "r", encoding="utf-8") as f:
    precedence_map = json.load(f)

response = supabase.table("clauses").select("id, clause_id, document, precedence_level").execute()
clauses = response.data

tagged = 0
skipped = 0
missing = 0

for idx, clause in enumerate(clauses):
    clause_id = clause.get("clause_id")
    doc = clause.get("document")
    current_level = clause.get("precedence_level")
    new_level = precedence_map.get(doc)

    if not clause_id or not doc or new_level is None:
        if VERBOSE:
            print(f"[WARN] Missing info for clause_id={clause_id}, doc={doc}")
        missing += 1
        continue

    if current_level != new_level:
        if VERBOSE:
            print(f"[UPDATE] {clause_id}: {current_level} → {new_level}")
        if not DRY_RUN:
            supabase.table("clauses").update({"precedence_level": new_level}).eq("clause_id", clause_id).execute()
        tagged += 1
    else:
        skipped += 1

    if idx % 100 == 0:
        print(f"...Processed {idx}/{len(clauses)}")

print("\n✅ Precedence tagging complete.")
print(f"🔍 Total clauses checked: {len(clauses)}")
print(f"🏷️ Tagged/Updated: {tagged}")
print(f"⏭️ Skipped (already correct): {skipped}")
print(f"⚠️ Missing or no matching document: {missing}")
