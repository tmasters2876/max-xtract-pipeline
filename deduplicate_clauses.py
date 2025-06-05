import json

def deduplicate_clauses(input_file="clauses_cleaned.json", output_file="clauses_deduped.json"):
    with open(input_file, "r") as f:
        clauses = json.load(f)

    seen = set()
    deduped = []

    for clause in clauses:
        clause_id = clause.get("clause_id")
        if clause_id and clause_id not in seen:
            seen.add(clause_id)
            deduped.append(clause)

    with open(output_file, "w") as f:
        json.dump(deduped, f, indent=2)

    print(f"✅ Deduplicated: {len(clauses) - len(deduped)} removed. {len(deduped)} clauses saved to {output_file}")

if __name__ == "__main__":
    deduplicate_clauses()
