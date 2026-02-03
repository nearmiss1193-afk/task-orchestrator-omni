
import requests
import os

# --- CONFIG ---
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjE5MTc1MiwiZXhwIjoyMDUxNzY3NzUyfQ.GvYAnL381xdX8D6jHpTYokgtTZfv6sv0FCAmlfGhug81xdX"

def verify_tasks():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    url = f"{SUPABASE_URL}/rest/v1/sovereign_tasks"
    params = {"order": "created_at.desc", "limit": 3}
    
    print("🛰️ Verifying Task Injection in Supabase...")
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            tasks = res.json()
            for t in tasks:
                print(f"✅ Found Task: {t.get('task_description')} | Status: {t.get('status')} | Created: {t.get('created_at')}")
        else:
            print(f"❌ Failed to query tasks: {res.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_tasks()
