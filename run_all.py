import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_FILE = "pages.json"
OUTPUT_FILE = "clauses_cleaned.json"

def parse_page_with_gpt(text, page, document):
    prompt = f"""
You are extracting enforceable clauses from a page of an HOA governing document.

Document: {document}
Page: {page}

Extract each clause with:
- clause_id (e.g. DECL_05_03)
- citation (article/section or best guess)
- clause_text (original excerpt)
- plain_summary (clear summary in plain English)
- tags (keywords, optional)

Format as a JSON array of objects.

Page Text:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract clauses from legal documents into structured JSON."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content

        if not content.strip().startswith("["):
            print(f"⚠️ GPT returned non-JSON content for {document} p{page}:")
            print(content.strip()[:200])
            return []

        clauses = json.loads(content)

        for clause in clauses:
            clause["document"] = document
            clause["page"] = page
            clause["link"] = None
            clause["embedding"] = None
            clause["match_source"] = "vector"
            clause["reviewer_id"] = None

        return clauses

    except Exception as e:
        print(f"❌ Error parsing page {document} p{page}: {e}")
        return []

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        pages = json.load(f)

    all_clauses = []
    for page in pages:
        clauses = parse_page_with_gpt(page["text"], page["page"], page["document"])
        all_clauses.extend(clauses)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_clauses, f, indent=2, ensure_ascii=False)

    print(f"✅ Parsed {len(all_clauses)} clauses to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
