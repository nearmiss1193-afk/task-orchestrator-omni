import os
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
import uuid

def migrate_leads():
    sb = get_supabase()
    
    # Fetch new leads from the old table
    res = sb.table("leads").select("*").eq("status", "new").execute()
    leads = res.data
    
    print(f"🔄 Migrating {len(leads)} leads to contacts_master (Bulk)...")
    
    to_insert = []
    for lead in leads:
        ghl_id = lead.get("ghl_contact_id") or f"SCRAPED_{lead['id'][:8]}"
        
        to_insert.append({
            "ghl_contact_id": ghl_id,
            "full_name": lead.get("company_name") or "Prospect",
            "email": lead.get("email"),
            "phone": lead.get("phone"),
            "website_url": lead.get("website_url"),
            "status": "new",
            "raw_research": lead.get("agent_research")
        })
    
    if to_insert:
        # Bulk upsert to handle duplicates on ghl_contact_id
        try:
            res = sb.table("contacts_master").upsert(to_insert, on_conflict="ghl_contact_id").execute()
            print(f"✅ Successfully migrated {len(to_insert)} leads.")
        except Exception as e:
            print(f"❌ Bulk Migration Failed: {e}")

if __name__ == "__main__":
    migrate_leads()
