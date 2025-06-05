import os
import json
from supabase import create_client
from dotenv import load_dotenv
from tqdm import tqdm
import openai

# === Load environment ===
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = OPENAI_API_KEY

# === Load document links ===
with open("document_links.json") as f:
    document_links = json.load(f)

# === Helpers ===
def get_link_from_doc_page(document, page):
    for entry in document_links:
        if entry["document_name"].strip() == document.strip() and entry["page"] == page:
            return entry["link"]
    return None

def generate_embedding(text):
    try:
        response = openai.Embedding.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"⚠️ Embedding error: {e}")
        return None

def patch_field(clause_id, field_name, value):
    try:
        res = supabase.table("clauses").update({field_name: value}).eq("clause_id", clause_id.strip()).execute()
        if res.status_code == 200:
            return True
    except Exception as e:
        print(f"❌ Failed to patch {field_name} for {clause_id}: {e}")
    return False

def verify_patch(clause_id, field):
    res = supabase.table("clauses").select(field).eq("clause_id", clause_id.strip()).execute()
    if res.data and field in res.data[0]:
        return res.data[0][field]
    return None

# === Main patching logic ===
def run_repair():
    print("🔧 Starting recovery (v3)...")
    data = supabase.table("clauses").select("*").execute()
    clauses = data.data

    patched = 0
    skipped = 0

    for clause in tqdm(clauses, desc="🔍 Repairing clauses"):
        clause_id = clause.get("clause_id", "").strip()
        document = clause.get("document", "").strip()
        page = clause.get("page")
        updates_made = False

        # Fix citation
        citation = clause.get("citation")
        if not citation or citation.strip() == "":
            success = patch_field(clause_id, "citation", "Auto")
            result = verify_patch(clause_id, "citation")
            if success and result == "Auto":
                updates_made = True
                print(f"✅ Patched citation for {clause_id}")

        # Fix link
        link = clause.get("link")
        if (not link or link.strip() == "") and document and page is not None:
            new_link = get_link_from_doc_page(document, page)
            if new_link:
                success = patch_field(clause_id, "link", new_link)
                result = verify_patch(clause_id, "link")
                if success and result == new_link:
                    updates_made = True
                    print(f"✅ Patched link for {clause_id}")

        # Fix page if blank string
        if isinstance(page, str) and page.strip() == "":
            success = patch_field(clause_id, "page", None)

        # Fix embedding
        embedding = clause.get("embedding")
        if not embedding and clause.get("summary"):
            new_embed = generate_embedding(clause["summary"])
            if new_embed:
                success = patch_field(clause_id, "embedding", new_embed)
                result = verify_patch(clause_id, "embedding")
                if success and result:
                    updates_made = True
                    print(f"✅ Patched embedding for {clause_id}")

        if updates_made:
            patched += 1
        else:
            skipped += 1

    print(f"\n🟩 Repair complete. Patched: {patched} | Skipped: {skipped}")

# === Entry ===
if __name__ == "__main__":
    run_repair()
