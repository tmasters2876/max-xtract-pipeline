import os
import requests
from supabase import create_client
from dotenv import load_dotenv

# Load .env secrets
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Fetch all unique document-link pairs
print("🔍 Fetching unique document-link pairs from Supabase...")
response = supabase.table("clauses").select("document, link").execute()
rows = response.data

# Use dict to deduplicate: { document: link }
document_links = {}
for row in rows:
    doc = row["document"]
    link = row["link"]
    document_links[doc] = link  # last link wins if duplicates

print(f"✅ Found {len(document_links)} unique documents to validate.\n")

# Validate each link with HEAD request
bad_links = []
for doc, link in document_links.items():
    try:
        r = requests.head(link, allow_redirects=True, timeout=10)
        if r.status_code == 200:
            print(f"✅ {doc} -> OK")
        else:
            print(f"❌ {doc} -> BAD HTTP {r.status_code} -> {link}")
            bad_links.append((doc, link, r.status_code))
    except Exception as e:
        print(f"❌ {doc} -> ERROR {e} -> {link}")
        bad_links.append((doc, link, str(e)))

# Summary
print("\n🔎 Validation Complete!")
print(f"✅ Valid links: {len(document_links) - len(bad_links)}")
print(f"❌ Bad links: {len(bad_links)}")

if bad_links:
    print("\n📌 Bad Links List:")
    for doc, link, issue in bad_links:
        print(f"- {doc}: {link} [Issue: {issue}]")
