import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

EXPECTED_FIELDS = [
    "clause_id",
    "document",
    "page",
    "citation",
    "clause_text",
    "plain_summary",
    "link",
    "embedding",
    "match_source",
    "reviewer_id",
    "tags",
    "created_at"
]

def check_schema():
    try:
        response = supabase.table("clauses").select("*").limit(1).execute()
        record = response.data[0] if response.data else {}

        missing_fields = [field for field in EXPECTED_FIELDS if field not in record]
        extra_fields = [field for field in record if field not in EXPECTED_FIELDS]

        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All expected fields present.")

        if extra_fields:
            print(f"⚠️ Extra (unexpected) fields: {extra_fields}")
        else:
            print("✅ No unexpected fields detected.")

    except Exception as e:
        print(f"❌ Error querying Supabase: {e}")

if __name__ == "__main__":
    check_schema()
