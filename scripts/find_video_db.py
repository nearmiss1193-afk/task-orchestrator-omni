
import os
import json
from modules.database.supabase_client import get_supabase

# Mock environment for local execution if needed
os.environ["SUPABASE_URL"] = "https://rzcpfwkygdvoshtwxncs.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def find_latest_video():
    supabase = get_supabase()
    res = supabase.table("contacts_master").select("company_name", "raw_research").order("last_outreach", desc=True).limit(20).execute()
    
    for lead in res.data:
        raw = lead.get("raw_research")
        if not raw: continue
        if isinstance(raw, str): raw = json.loads(raw)
        
        drafts = raw.get("social_drafts", [])
        for d in drafts:
            if d.get("status") == "published" and d.get("video_url"):
                print(f"FOUND: {lead['company_name']}")
                print(f"PLATFORM: {d['platform']}")
                print(f"URL: {d['video_url']}")
                return

if __name__ == "__main__":
    find_latest_video()
