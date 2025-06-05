import os
import json
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

# === Load credentials ===
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Load document link mapping ===
with open("document_links.json", "r", encoding="utf-8") as f:
    doc_links = json.load(f)

# === Utility: handle blank, empty, or None values
def is_missing(value):
    return value is None or (isinstance(value, str) and value.strip() == "")

# === Generate document link
def generate_link(document_name, page):
    base = doc_links.get(document_name)
    return f"{base}#page={page or 1}" if base else None

# === Regenerate OpenAI embedding
def regenerate_embedding(text):
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

# === Main repair logic ===
def patch_clauses():
    response = supabase.table("clauses").select("*").execute()
    clauses = response.data
    updated = 0

    print(f"\n📦 Retrieved {len(clauses)} clauses from Supabase.\n")

    if not clauses:
        print("❌ No clauses found — check table name or API access.")
        return

    print(f"🔍 Sample clause ID: {clauses[0].get('clause_id')}")

    for clause in clauses:
        clause_id = clause.get("clause_id")
        document = clause.get("document")
        page = clause.get("page")
        summary = clause.get("summary", "")
        link = clause.get("link")
        citation = clause.get("citation")
        embedding = clause.get("embedding")

        updates = {}
        reasons = []

        # 🔗 Rebuild link
        if is_missing(link) and document:
            new_link = generate_link(document, page)
            if new_link:
                updates["link"] = new_link
                reasons.append("link")

        # 📚 Rebuild citation
        if is_missing(citation) and page:
            updates["citation"] = f"Page {page}"
            reasons.append("citation")

        # 🧠 Regenerate embedding
        if not embedding and summary.strip():
            emb = regenerate_embedding(summary)
            if emb:
                updates["embedding"] = emb
                reasons.append("embedding")

        # ⚠️ Skip logging
        if not updates:
            print(f"⏭️  Skipped: {clause_id}")
        else:
            print(f"🔧 Updating {clause_id} → {reasons}")
            supabase.table("clauses").update(updates).eq("clause_id", clause_id).execute()
            updated += 1

    print(f"\n✅ Repair complete. Total clauses updated: {updated}")

# === Run ===
if __name__ == "__main__":
    patch_clauses()
