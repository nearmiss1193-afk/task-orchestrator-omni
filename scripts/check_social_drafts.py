
from modules.database.supabase_client import get_supabase
import json

def check_drafts():
    supabase = get_supabase()
    res = supabase.table("contacts_master").select("id", "company_name", "raw_research").execute()
    leads = res.data
    
    draft_count = 0
    for lead in leads:
        raw = json.loads(lead.get("raw_research") or "{}")
        drafts = raw.get("social_drafts", [])
        for d in drafts:
            if d.get("status") == "draft":
                print(f"Lead: {lead['company_name']} ({lead['id']}) - Platform: {d['platform']}")
                draft_count += 1
                
    print(f"\nTotal drafts found: {draft_count}")

if __name__ == "__main__":
    check_drafts()
