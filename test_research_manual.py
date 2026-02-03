import modal
from dotenv import load_dotenv
import os

load_dotenv()

def test_research():
    # Get a contact_id
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
    res = sb.table("contacts_master").select("ghl_contact_id").not_.eq("website_url", "").limit(1).execute()
    if not res.data:
        print("No 'new' leads found.")
        return
    
    contact_id = res.data[0]['ghl_contact_id']
    print(f"Testing research for: {contact_id}")
    
    # Trigger research_lead_logic via modal
    f = modal.Function.from_name("nexus-outreach-v1", "research_lead_logic")
    result = f.remote(contact_id)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_research()
