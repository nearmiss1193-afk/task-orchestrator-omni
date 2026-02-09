
import os
import json
from modules.database.supabase_client import get_supabase

def audit_leads():
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase client initialization failed.")
        return

    try:
        res = supabase.table('contacts_master').select('*', count='exact').limit(10).execute()
        print(f"Total Leads in contacts_master: {res.count}")
        
        leads = res.data
        for l in leads:
            print(f"ID: {l.get('id')} | Name: {l.get('full_name')} | Status: {l.get('status')} | GHL ID: {l.get('ghl_id')} | GHL contact_id: {l.get('ghl_contact_id')}")
            
    except Exception as e:
        print(f"❌ Lead audit failed: {e}")

if __name__ == "__main__":
    # Ensure environment variables are loaded or use the ones from the vault if local
    # For local testing, we might need to source them
    audit_leads()
