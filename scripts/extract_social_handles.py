
import json
from modules.database.supabase_client import get_supabase

def extract_handles():
    sb = get_supabase()
    # Query latest leads with research done
    res = sb.table("contacts_master").select("company_name,raw_research").eq("status", "research_done").limit(10).execute()
    
    if not res.data:
        print("No leads found with 'research_done' status.")
        return
        
    print("\n--- SOCIAL HANDLE EXTRACTION ---")
    for lead in res.data:
        company = lead.get("company_name")
        raw_research = lead.get("raw_research")
        if not raw_research:
            continue
            
        try:
            if isinstance(raw_research, str):
                raw = json.loads(raw_research)
            else:
                raw = raw_research
                
            drafts = raw.get("social_drafts", [])
            if not drafts:
                continue
                
            print(f"\n🏢 {company}:")
            found = False
            for d in drafts:
                plat = d.get("platform")
                if plat in ["facebook", "instagram", "linkedin", "twitter"]:
                    handle = d.get("handle") or d.get("post_url") or "Linked to Ayrshare Account"
                    print(f"  - {plat.upper()}: {handle}")
                    found = True
            if not found:
                print("  No FB/IG handles found in drafts.")
        except Exception as e:
            print(f"Error parsing draft for {company}: {e}")

if __name__ == "__main__":
    extract_handles()
