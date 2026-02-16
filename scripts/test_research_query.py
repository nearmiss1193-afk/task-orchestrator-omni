import os, json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_query():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    
    # Attempt the exact query from deploy.py
    try:
        res = supabase.table("contacts_master").select("*").eq("status", "new").not_.is_("website_url", "null").limit(2).execute()
        print(f"Query returned {len(res.data)} leads.")
        if res.data:
            [print(f"  {l['id']} | {l['website_url']}") for l in res.data]
    except Exception as e:
        print(f"Query A failed: {e}")
        
    # Attempt alternative query
    try:
        res = supabase.table("contacts_master").select("*").eq("status", "new").neq("website_url", None).limit(2).execute()
        print(f"\nQuery B (neq) returned {len(res.data)} leads.")
    except Exception as e:
        print(f"Query B failed: {e}")

if __name__ == "__main__":
    test_query()
