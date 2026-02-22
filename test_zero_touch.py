import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from workers.zero_touch_onboarding import parse_contact_status

# Ensure env vars are loaded
if not os.environ.get("SUPABASE_URL"):
    from dotenv import load_dotenv
    load_dotenv()

from modules.database.supabase_client import get_supabase
sb = get_supabase()

print("Fetching a test lead to trigger onboarding...")
res = sb.table("contacts_master").select("id, ghl_contact_id, company_name, email").not_.is_("ghl_contact_id", "null").not_.is_("email", "null").limit(1).execute()

if res.data:
    lead = res.data[0]
    contact_id = lead["ghl_contact_id"]
    print(f"Triggering for {lead['company_name']} (GHL ID: {contact_id}) (Email: {lead['email']})")
    
    # Reset the onboarding_status so it actually runs
    sb.table("contacts_master").update({"onboarding_status": {"is_fulfilled": False}}).eq("ghl_contact_id", contact_id).execute()
    
    # Run the sequence
    result = parse_contact_status(contact_id)
    print("Zero-touch sequence result:", result)
else:
    print("No testable lead found with a ghl_contact_id and email.")
