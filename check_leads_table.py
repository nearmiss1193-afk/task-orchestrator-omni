
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def check_leads_table():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("Checking 'leads' table...")
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads?limit=1",
        headers=headers,
        timeout=10
    )
    
    if res.status_code == 200:
        print("✅ Table 'leads' exists and is accessible.")
        return True
    else:
        print(f"❌ Table 'leads' check failed. Status: {res.status_code}")
        print(res.text)
        return False

if __name__ == "__main__":
    check_leads_table()
