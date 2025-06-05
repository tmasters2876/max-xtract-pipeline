import os
import json
from dotenv import load_dotenv
from supabase import create_client
from tqdm import tqdm
import openai

# === Load environment ===
load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Load document links ===
with open("document_links.json") as f:
    document_links = json.load(f)

# === Link Builder ===
def get_link(document, page):
    base = document_links.get(document)
    return f"{base}#page={page}" if base and page is not None else None

# === Embedding Generator ===
def get_embedding(text):
    try:
        result = openai.Embedding.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        return result["data"][0]["embedding"]
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

# === Patch Utility ===
def patch_clause(clause_id, field, value):
    try:
        supabase.table("clauses").update({field: value}).eq("clause_id", clause_id).execute()
        print(f"✅ Patched {field} for {clause_id}")
        return True
    except Exception as e:
        print(f"❌ Patch failed for {field} on {clause_id}: {e}")
        return False

# === Dirty Value Detector ===
def is_bad(value):
    return value is None or str(value).strip().lower() in ["", "n/a", "null"]

# === Repair Execution ===
def run_repair():
    print("\n🔍 Fetching clauses from Supabase...")
    result = supabase.table("clauses").select("*").execute()
    clauses = result.data

    if not clauses:
        print("❌ No clauses found.")
        return

    patched = 0
    skipped = 0

    for clause in tqdm(clauses, desc="🔧 Repairing"):
        cid = clause.get("clause_id", "").strip()
        doc = clause.get("document", "").strip()
        page = clause.get("page")
        summary = clause.get("summary", "")

        updated = False

        # 🔗 Fix link
        if is_bad(clause.get("link")) and doc and page is not None:
            new_link = get_link(doc, page)
            if new_link:
                if patch_clause(cid, "link", new_link):
                    updated = True

        # 📚 Fix citation
        if is_bad(clause.get("citation")):
            guess = f"Page {page}" if page else "Auto"
            if patch_clause(cid, "citation", guess):
                updated = True

        # 🧠 Fix embedding
        if not clause.get("embedding") and summary.strip():
            emb = get_embedding(summary)
            if emb:
                if patch_clause(cid, "embedding", emb):
                    updated = True

        if updated:
            patched += 1
        else:
            skipped += 1
            print(f"\n⏩ Skipped {cid}")
            print(f"   └ link:     {clause.get('link')}")
            print(f"   └ citation: {clause.get('citation')}")
            print(f"   └ embedding: {'✅' if clause.get('embedding') else '❌'}")

            print(f"⏩ Skipped {cid}: all fields present or already valid.")

    print(f"\n✅ Repair complete. Patched: {patched} | Skipped: {skipped}")

# === Entry Point ===
if __name__ == "__main__":
    run_repair()
