import sys
import os
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv('.env.local')

from execution.v2.stripe_webhook import executes_logic
from execution.v2.test_first_contact import verify_system_action
# Note: test_first_contact was deleted, but I can re-create logic.

def test_stripe_flow():
    print("🧪 [TEST] Testing Revenue Loop...")
    
    # Mock Data
    test_email = "test.vanderbilt.stripe@example.com"
    amount = 997.00
    
    # 1. Ensure contact exists (Reuse creating logic or just check)
    from supabase import create_client
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)
    # Cleanup first
    try:
        supabase.table("contacts_master").delete().eq("email", test_email).execute()
        supabase.table("contacts_master").delete().eq("ghl_contact_id", "stripe_test_001").execute()
    except:
        pass

    # Upsert test contact
    lead = {
        "ghl_contact_id": "stripe_test_001",
        "email": test_email,
        "full_name": "Stripe Payer",
        "status": "new",
        "website_url": "stripe-test.example.com",
        "raw_research": {"source": "manual_test_stripe"}
    }
    try:
        supabase.table("contacts_master").upsert(lead, on_conflict="email").execute()
        print("✅ Pre-test: Created/Reset lead 'Stripe Payer'")
    except Exception as e:
        print(f"❌ Setup Failed: {e}")
        return

    # 2. Trigger Logic
    print("💸 Simulating Payment...")
    executes_logic(test_email, amount)
    
    # 3. Verify
    print("\n🔍 Verifying Outcome...")
    res = supabase.table("contacts_master").select("*").eq("email", test_email).execute()
    data = res.data[0]
    
    if data.get('status') == 'customer':
        print(f"✅ SUCCESS: Lead converted to CUSTOMER (Value: {data.get('last_order_value')})")
    else:
        print(f"❌ FAIL: Status is '{data.get('status')}'")

if __name__ == "__main__":
    test_stripe_flow()
