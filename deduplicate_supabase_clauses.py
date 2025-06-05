import os
from supabase import create_client
from dotenv import load_dotenv

# === Load Environment Variables ===
load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# === Deduplicate Clauses in Supabase Based on clause_id ===
def deduplicate_supabase_clauses():
    print("🔍 Fetching all clauses...")
    result = supabase.table("clauses").select("*").execute()

    if not result.data:
        print("⚠️ No data found.")
        return

    seen_clause_ids = {}
    duplicates_to_delete = []

    for row in result.data:
        cid = row.get("clause_id")
        row_id = row.get("id")

        if cid:
            if cid not in seen_clause_ids:
                seen_clause_ids[cid] = row_id
            else:
                duplicates_to_delete.append(row_id)

    print(f"🧹 Found {len(duplicates_to_delete)} duplicates to delete.")

    for id in duplicates_to_delete:
        try:
            supabase.table("clauses").delete().eq("id", id).execute()
        except Exception as e:
            print(f"❌ Failed to delete row ID {id}: {e}")

    print(f"✅ Deduplication complete. {len(duplicates_to_delete)} duplicates removed.")

if __name__ == "__main__":
    deduplicate_supabase_clauses()
