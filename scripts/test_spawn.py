import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from workers.outreach import dispatch_audit_email
from modules.database.supabase_client import get_supabase

def test_spawn():
    print("Testing dispatch_audit_email spawn...")
    supabase = get_supabase()
    
    # get a lead that is in audit_processing
    res = supabase.table("contacts_master").select("*").eq("status", "audit_processing").limit(1).execute()
    if not res.data:
        print("No leads in audit_processing. Let's find a 'new' lead with a website.")
        res = supabase.table("contacts_master").select("*").eq("status", "new").not_.is_("website_url", "null").limit(1).execute()
        
    if not res.data:
        print("No suitable leads found.")
        return
        
    lead = res.data[0]
    lead_id = lead["id"]
    print(f"Triggering for lead {lead_id} - {lead.get('company_name')} - {lead.get('website_url')}")
    
    try:
        # We will call it locally instead of spawn so we can see the exact error trace in the console!
        print("Calling .local() to catch the error inline...")
        result = dispatch_audit_email.local(lead_id)
        print("Result:", result)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_spawn()
