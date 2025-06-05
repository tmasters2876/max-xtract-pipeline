import os
from dotenv import load_dotenv
from supabase import create_client

# === Load Supabase credentials ===
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

# === Required Fields ===
REQUIRED_FIELDS = [
    "clause_id", "summary", "original_text", "citation", "document",
    "page", "tags", "arc_relevant", "concern_level", "link", "embedding"
]

# === QA Logic ===
def qa_check_supabase():
    print("🔍 Running QA check against Supabase...")
    result = supabase.table("clauses").select("*").execute()

    clauses = result.data
    issues = []

    print(f"📦 Loaded {len(clauses)} clauses from Supabase.\n")

    for i, clause in enumerate(clauses):
        missing = []
        for field in REQUIRED_FIELDS:
            if field not in clause or clause[field] in [None, "", []]:
                missing.append(field)
        if missing:
            issues.append({
                "index": i + 1,
                "clause_id": clause.get("clause_id", "❓ Unknown"),
                "document": clause.get("document"),
                "page": clause.get("page"),
                "missing": missing
            })

    if issues:
        with open("qa_supabase_issues.log", "w", encoding="utf-8") as log:
            for issue in issues:
                log.write(
                    f"[Clause {issue['index']}] {issue['clause_id']} "
                    f"(Document: {issue['document']} Page: {issue['page']}) "
                    f"- Missing: {', '.join(issue['missing'])}\n"
                )
        print(f"⚠️ Found {len(issues)} problematic clauses. See qa_supabase_issues.log.")
    else:
        print("✅ All clauses passed QA validation.")

# === Execute ===
if __name__ == "__main__":
    qa_check_supabase()
