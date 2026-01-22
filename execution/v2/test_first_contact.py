import asyncio
import sys
import os
import uuid
# Ensure we can import from root
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env.local')

from supabase import create_client
from execution.v2.v2_orchestrator import Orchestrator

def verify_system_action():
    print("🧪 [TEST] Initiating First Contact verification...")
    
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Missing Creds")
        return

    supabase = create_client(url, key)
    
    # 1. Create Mock Lead
    test_id = str(uuid.uuid4())
    lead = {
        "ghl_contact_id": f"test_{test_id[:8]}",
        "full_name": "Test Vanderbilt",
        "email": f"test.vanderbilt.{test_id[:4]}@example.com",
        "phone": "+15550199999",
        "status": "new",
        "lead_score": 85,
        "website_url": "vanderbilt-test.example.com",
        "raw_research": {"source": "manual_test_v2"},
        "ai_strategy": "Manual Insertion Test"
    }
    
    try:
        # Check if contacts_master exists or lead table details
        # Assuming contacts_master schema from previous context
        print("Creating test lead...")
        supabase.table("contacts_master").insert(lead).execute()
        print(f"✅ Lead Created: {lead['email']} (Score: 85)")
    except Exception as e:
        print(f"❌ Failed to create lead: {e}")
        return

    # 2. Run Orchestrator
    print("\n🧠 Invoking Orchestrator...")
    orch = Orchestrator()
    orch.sense_and_act()
    
    # 3. Verify Mutation
    print("\n🔍 Verifying Outcome...")
    res = supabase.table("contacts_master").select("*").eq("ghl_contact_id", lead['ghl_contact_id']).execute()
    
    if not res.data:
        print("❌ Lead not found in DB")
        return

    data = res.data[0]
    
    if data['status'] == 'contacted_sms':
        print(f"✅ SUCCESS: Lead status changed to '{data['status']}'")
        print(f"   Last Outreach: {data.get('last_outreach_at')}")
    else:
        print(f"❌ FAIL: Lead status is '{data['status']}' (Expected 'contacted_sms')")

if __name__ == "__main__":
    verify_system_action()
