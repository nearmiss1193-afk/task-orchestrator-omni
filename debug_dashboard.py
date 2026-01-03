
import os
from supabase import create_client
import json

# HARDCODED SECRETS (From deploy.py)
URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def get_supabase():
    return create_client(URL, KEY)

def test_leads():
    print("--- TESTING LEADS ENDPOINT ---")
    try:
        supabase = get_supabase()
        # Exact logic from dashboard_service.py
        raw = supabase.table("contacts_master").select("*").order("created_at", desc=True).limit(20).execute().data
        
        print(f"Fetched {len(raw)} rows.")
        if len(raw) > 0:
            print(f"Sample Row: {raw[0]}")
            
        grid_data = []
        for r in raw:
            tags = r.get("tags") or []
            campaign = "Cold Outreach V1" if "risk_high" in tags else "Inbound Waitlist"
            
            industry_map = ["Real Estate", "SaaS", "E-commerce", "Local Biz", "Healthcare"]
            # Check for possible TypeError in hash logic
            cid = r.get("ghl_contact_id", "")
            if not isinstance(cid, str):
                cid = str(cid)
                
            pseudo_random_index = len(cid) % len(industry_map)
            sector = industry_map[pseudo_random_index]
            
            grid_data.append({
                "name": r.get("full_name") or "Unknown Target",
                "industry": sector,
                "campaign": campaign,
                "status": r.get("status"),
                "score": r.get("lead_score") or 50
            })
        print(f"Refined Data: {json.dumps(grid_data[:2])}")
        print("✅ SUCCESS")
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_leads()
