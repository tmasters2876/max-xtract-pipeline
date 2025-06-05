# test_summary_query.py
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

res = supabase.from_("clauses").select("*").ilike("summary", "%fence%").execute()
print(res)
