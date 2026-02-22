import os
from supabase import create_client

def inspect():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    sb = create_client(url, key)
    
    # Check system_state for scraping queries
    res = sb.table("system_state").select("*").execute()
    print("System State Table:", res.data)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.secrets', 'secrets.env'))
    inspect()
