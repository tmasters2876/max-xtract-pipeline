from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

data = supabase.table("clauses").select("clause_id").limit(10).execute()
print(f"✅ Sample Clauses: {[row['clause_id'] for row in data.data]}")

count = supabase.table("clauses").select("*", count="exact").execute()
print(f"✅ Total Clauses in Supabase: {count.count}")

