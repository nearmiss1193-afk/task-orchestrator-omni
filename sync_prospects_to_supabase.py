
import os
import json
import time
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sync_prospects():
    json_path = "campaign_prospects.json"
    
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        prospects = json.load(f)

    print(f"📦 Found {len(prospects)} prospects to sync...")
    
    count = 0
    for p in prospects:
        # Map JSON fields to DB columns
        data = {
            "first_name": p.get('name', '').split(' ')[0],
            "last_name": ' '.join(p.get('name', '').split(' ')[1:]) if ' ' in p.get('name', '') else '',
            "company_name": p.get('company'),
            "email": p.get('email'),
            "phone": p.get('phone'),
            "city": p.get('city'),
            "state": "FL",
            "industry": p.get('industry', 'HVAC'),
            "source": "grok_hunter_v1",
            "status": "new",
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S%z')
        }
        
        # Check if exists (dedupe by email or company)
        existing = None
        if data['email']:
            res = supabase.table('leads').select('id').eq('email', data['email']).execute()
            if res.data: existing = res.data[0]
            
        if not existing and data['company_name']:
             res = supabase.table('leads').select('id').eq('company_name', data['company_name']).execute()
             if res.data: existing = res.data[0]

        try:
            if existing:
                print(f"  Existing: {data['company_name']}")
                # Optional: Update?
            else:
                supabase.table('leads').insert(data).execute()
                print(f"  ✅ Inserted: {data['company_name']}")
                count += 1
        except Exception as e:
            print(f"  ❌ Error syncing {data['company_name']}: {e}")

    print(f"Synced {count} new leads.")

if __name__ == "__main__":
    sync_prospects()
