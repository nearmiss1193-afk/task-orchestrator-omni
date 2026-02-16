
from modules.database.supabase_client import get_supabase
import json

def find_social_touch():
    supabase = get_supabase()
    # Check outbound_touches for today's social posts
    res = supabase.table("outbound_touches").select("*").eq("channel", "social").order("ts", desc=True).limit(1).execute()
    
    if res.data:
        touch = res.data[0]
        meta = touch.get("metadata") or {}
        if isinstance(meta, str): meta = json.loads(meta)
        
        print(f"\n✅ VERIFIED SOCIAL POST")
        print(f"Timestamp: {touch['ts']}")
        print(f"Platform: {meta.get('platform', 'Unknown')}")
        print(f"Lead ID: {touch.get('contact_id')}")
        
        # Follow back to lead to get the video URL
        lead_res = supabase.table("contacts_master").select("company_name", "raw_research").eq("id", touch["contact_id"]).execute()
        if lead_res.data:
            lead = lead_res.data[0]
            raw = lead.get("raw_research")
            if isinstance(raw, str): raw = json.loads(raw)
            print(f"Company: {lead['company_name']}")
            print(f"Video URL: {raw.get('video_teaser_url')}")
    else:
        print("📭 No social touches found in outreach history today.")

if __name__ == "__main__":
    find_social_touch()
