import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

LOG_FILE = "qa_supabase_issues.log"

REQUIRED_FIELDS = [
    "clause_id", "document", "page", "citation", "clause_text",
    "plain_summary", "link", "embedding", "match_source"
]

INVALID_MARKERS = ["", "null", "None", None]

def validate_clause(clause):
    issues = []

    for field in REQUIRED_FIELDS:
        val = clause.get(field)
        if val in INVALID_MARKERS:
            issues.append(f"Missing or invalid: {field}")

    # Check link format
    link = clause.get("link", "")
    if link and not str(link).startswith("http"):
        issues.append("Malformed link")

    # Check citation format (basic heuristic)
    citation = clause.get("citation", "")
    if citation and not any(citation.lower().startswith(p) for p in ["art", "sec", "page"]):
        issues.append("Citation may be unstructured")

    return issues

def main():
    response = supabase.table("clauses").select("*").execute()
    records = response.data

    failed = []
    for clause in records:
        issues = validate_clause(clause)
        if issues:
            failed.append({
                "clause_id": clause.get("clause_id", "UNKNOWN"),
                "issues": issues
            })

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for item in failed:
            f.write(f"Clause {item['clause_id']} → {', '.join(item['issues'])}\n")

    print(f"✅ QA complete. {len(failed)} issue(s) written to {LOG_FILE}")

if __name__ == "__main__":
    main()
