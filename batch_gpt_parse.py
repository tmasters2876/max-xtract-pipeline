import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_FILE = "pages.json"
OUTPUT_FILE = "clauses_cleaned.json"

def parse_clauses(pages):
    results = []
    for page in pages:
        prompt = f"""
You are extracting enforceable clauses from a page of an HOA governing document.

Document: {page['document']}
Page: {page['page']}

Extract each clause with:
- clause_id (e.g. DECL_05_03)
- citation (e.g. "Article X, Section Y", or "Page Z", or similar)
- clause_text (verbatim excerpt)
- plain_summary (summary in plain English)
- tags (optional)

Return a JSON array of objects.

Page Text:
\"\"\"
{page['text']}
\"\"\"
""".strip()

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You extract structured clauses from legal documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            content = response.choices[0].message.content.strip()

            # Strip any triple backticks or markdown
            if content.startswith("```"):
                content = re.sub(r"^```json", "", content)
                content = re.sub(r"^```", "", content)
                content = re.sub(r"```$", "", content)
                content = content.strip()

            clauses = json.loads(content)

            for clause in clauses:
                clause["document"] = page["document"]
                clause["page"] = page["page"]
                clause["link"] = None
                clause["embedding"] = None
                clause["match_source"] = "vector"
                clause["reviewer_id"] = None

            results.extend(clauses)

        except Exception as e:
            print(f"❌ Error parsing page {page['document']} p{page['page']}: {e}")

    return results

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        pages = json.load(f)

    parsed_clauses = parse_clauses(pages)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(parsed_clauses, f, indent=2, ensure_ascii=False)

    print(f"✅ Parsed {len(parsed_clauses)} clauses to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
