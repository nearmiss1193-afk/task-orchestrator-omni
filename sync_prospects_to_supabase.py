
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

import sys

def sync_prospects(filename="campaign_prospects.json"):
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return

    with open(filename, 'r') as f:
        prospects = json.load(f)

    print(f"📦 Found {len(prospects)} prospects in {filename}...")
    
    count = 0
    for p in prospects:
        # Map JSON fields to DB columns
        # Schema adaptation: Phone, City, Industry go into 'agent_research' JSONB
        state = p.get('state', 'FL')
        prospect_data = {
            "first_name": p.get('name', '').split(' ')[0],
            "last_name": ' '.join(p.get('name', '').split(' ')[1:]) if ' ' in p.get('name', '') else '',
            "phone": p.get('phone'),
            "city": p.get('city'),
            "state": state,
            "industry": p.get('industry', 'HVAC'),
            "source": f"grok_hunter_{filename}"
        }

        data = {
            "company_name": p.get('company') or p.get('company_name'),
            "email": p.get('email'),
            "status": "new",
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S%z'),
            "agent_research": prospect_data # Store everything here
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

    print(f"Synced {count} new leads from {filename}.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        sync_prospects(sys.argv[1])
    else:
        sync_prospects()
