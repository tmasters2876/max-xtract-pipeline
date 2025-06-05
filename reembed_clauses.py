import os
from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

# Step 1: Pull all clauses
data = supabase.table("clauses").select("*").execute()
clauses = data.data

# Step 2: Rebuild embeddings using summary + original + tags
for clause in clauses:
    clause_id = clause["clause_id"]
    summary = clause.get("summary", "")
    original = clause.get("original_text", "")
    tags = clause.get("tags", [])

    input_text = f"{summary}\n{original}\nTags: {', '.join(tags)}"
    try:
        embed = client.embeddings.create(
            input=[input_text],
            model="text-embedding-ada-002"
        )
        vector = embed.data[0].embedding

        # Step 3: Update the row
        supabase.table("clauses").update({"embedding": vector}).eq("clause_id", clause_id).execute()
        print(f"✅ Updated embedding for {clause_id}")
    except Exception as e:
        print(f"❌ Error embedding {clause_id}: {e}")
