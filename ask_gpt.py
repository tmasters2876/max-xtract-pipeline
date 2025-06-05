import os
import json
import numpy as np
from openai import OpenAI
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env vars
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

TOP_N = 3

# --- Embed the user question ---
def embed_question(question):
    response = client.embeddings.create(
        input=[question],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# --- Cosine similarity function ---
def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# --- Fetch clauses from Supabase ---
def fetch_clauses():
    result = supabase.table("clauses").select("*").execute()
    return result.data

# --- Inject matched clauses into a GPT prompt ---
def generate_prompt(question, clauses):
    clause_text = "\n".join([
        f"### Clause Match {i+1}:\n"
        f"- **Summary:** {clause['summary']}\n"
        f"- **Full Text:** {clause['original_text']}\n"
        f"- **Citation:** {clause['citation']} (from *{clause['document']}*)\n"
        f"- **Link:** {clause['link']}\n"
        for i, clause in enumerate(clauses)
    ])

    return f"""
Answer the following question clearly and definitively using the clauses below.

Start by referencing the specific area asked about (e.g., front yard). If the rules **do not specify** a requirement for that context, say so clearly, and cite what the documents **do specify instead**.


Answer the following question clearly and definitively using the clauses below.

If the rules **do not specify a requirement**, say so clearly. If a requirement **is implied**, say that with justification. Always cite the specific clause(s), including **article/section**, **page**, and **document name**.

Respond in this format:

---
### 🧾 Final Answer:
<Your explanation here. Start with “The governing documents do not explicitly require...” or “The governing documents state that…”>

---

### 🔍 Supporting Clauses:
{clause_text}

---

### 🧠 Helpful Tip:
If the answer is unclear, you may suggest the user consult their HOA or ARC for clarification.
"""


# --- Main answer function ---
def answer_question(question):
    question_vec = embed_question(question)
    clauses = fetch_clauses()

    # Score and sort
    scored = []
    for clause in clauses:
        embedding = json.loads(clause["embedding"]) if isinstance(clause["embedding"], str) else clause["embedding"]
        similarity = cosine_similarity(question_vec, embedding)
        scored.append((similarity, clause))

    top_matches = [c for _, c in sorted(scored, key=lambda x: x[0], reverse=True)[:TOP_N]]

    # Generate GPT prompt
    prompt = generate_prompt(question, top_matches)

    # Debugging output
    # print(f"[DEBUG] Question sent to GPT: {question}")

    # Call GPT-4
    response = client.chat.completions.create(
        model="gpt-4o",  # You can also try "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful HOA policy assistant."},
            { "role": "user", "content": f"{question}\n\n{prompt}" }

        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# --- Example run ---
if __name__ == "__main__":
    user_question = "Do I need a see-through fence if installed in the front of my property?"
    answer = answer_question(user_question)
    print("\n🧠 Final Answer:\n")
    print(answer)
    
