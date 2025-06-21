import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

# Connect
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

# Load correct document → link map
with open("document_links.json") as f:
    doc_links = json.load(f)

# For each document, update ALL matching rows
for document, link in doc_links.items():
    response = supabase.table("clauses").update({"link": link}).eq("document", document).execute()
    print(f"Updated '{document}' link to: {link} — Affected rows: {response}")
