import os
import json
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

INPUT_FILE = "clauses_cleaned.json"

# === Load Document Links ===
with open("document_links.json", "r", encoding="utf-8") as f:
    document_links = json.load(f)

# === Fetch existing Clause IDs from Supabase ===
def fetch_existing_clause_ids():
    try:
        result = supabase.table("clauses").select("clause_id").execute()
        return {row["clause_id"] for row in result.data}
    except Exception as e:
        print(f"❌ Failed to fetch existing clause_ids: {e}")
        return set()

# === Get embedding from OpenAI ===
def get_embedding(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

# === Upload Clauses ===
def upload_clauses():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        clauses = json.load(f)

    existing_ids = fetch_existing_clause_ids()
    count = 0

    for clause in clauses:
        if not clause.get("clause_id") or not clause.get("plain_summary"):
            continue

        # 🔄 Generate embedding
        clause["embedding"] = get_embedding(clause["plain_summary"])
        if not clause["embedding"]:
            continue

        # ✅ Ensure required defaults
        clause.setdefault("match_source", "vector")
        clause.setdefault("reviewer_id", None)
        clause.setdefault("tags", [])

        # ✅ Inject raw document link from document_links.json
        link = document_links.get(clause["document"])
        clause["link"] = link if link else None

        # 📦 Prepare payload
        data = {
            "clause_id": clause["clause_id"],
            "document": clause["document"],
            "page": clause["page"],
            "citation": clause["citation"],
            "clause_text": clause["clause_text"],
            "plain_summary": clause["plain_summary"],
            "link": clause["link"],
            "embedding": clause["embedding"],
            "match_source": clause["match_source"],
            "reviewer_id": clause["reviewer_id"],
            "tags": clause["tags"]
        }

        try:
            # 🔄 Upsert by clause_id
            supabase.table("clauses").upsert(data, on_conflict="clause_id").execute()
            count += 1
        except Exception as e:
            print(f"❌ Upload failed for {clause['clause_id']}: {e}")

    print(f"✅ Uploaded or updated {count} clauses to Supabase")

if __name__ == "__main__":
    upload_clauses()
