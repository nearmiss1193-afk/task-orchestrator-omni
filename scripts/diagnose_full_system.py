import os
import asyncio
import requests
from supabase import create_client

# Setup Supabase
URL = os.environ.get("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo")
supabase = create_client(URL, KEY)

def check_leads():
    print("\n--- 1. LEAD STATUS ANALYSIS ---")
    try:
        # Group by status
        res = supabase.table("contacts_master").select("*").execute()
        leads = res.data
        status_counts = {}
        score_buckets = {"0": 0, "1-69": 0, "70+": 0}
        
        for l in leads:
            s = l.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
            
            score = l.get("lead_score", 0) or 0
            if score == 0: score_buckets["0"] += 1
            elif score < 70: score_buckets["1-69"] += 1
            else: score_buckets["70+"] += 1
            
        print(f"Total Leads: {len(leads)}")
        print(f"Status Breakdown: {status_counts}")
        print(f"Score Breakdown: {score_buckets}")
        
        # Previous Filter Impact
        blocked_by_status = status_counts.get("research_done", 0) + status_counts.get("contacted", 0)
        blocked_by_score = score_buckets["0"] + score_buckets["1-69"]
        print(f"POTENTIAL BLOCKER FOUND: Old filter required status='new' (only {status_counts.get('new', 0)} leads) and score>70 ({score_buckets['70+']} leads).")
        
    except Exception as e:
        print(f"Error checking leads: {e}")

def check_endpoints():
    print(f"\n--- 2. ENDPOINT HEALTH CHECK ---", flush=True)
    endpoints = [
        "https://nearmiss1193--ghl-omni-automation-empire-dashboard.modal.run",
        "https://nearmiss1193-afk--ghl-omni-automation-empire-dashboard.modal.run",
        "https://nearmiss1193--ghl-omni-automation-fastapi-app.modal.run", 
    ]
    
    for ep in endpoints:
        try:
            r = requests.get(ep, timeout=5)
            print(f"{ep}: {r.status_code}", flush=True)
        except Exception as e:
            print(f"{ep}: Failed ({str(e)[:50]})", flush=True)

def check_database_activity():
    print("\n--- 3. RECENT ACTIVITY ---")
    try:
        touches = supabase.table("outbound_touches").select("*").order("created_at", desc=True).limit(5).execute()
        print(f"Recent Touches: {len(touches.data)}")
        for t in touches.data:
            print(f" - {t.get('created_at')}: {t.get('channel')}")
            
        interactions = supabase.table("interactions").select("*").limit(5).execute()
        print(f"Interactions Table Count: {len(interactions.data)} (If 0, webhooks are failing)")
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == "__main__":
    check_leads()
    check_endpoints()
    check_database_activity()
