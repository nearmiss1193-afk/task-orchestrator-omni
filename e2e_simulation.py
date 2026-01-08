import os
import time
import uuid
import json
import requests
from modules import billing
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Setup
env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(env_path)
if not os.getenv("SUPABASE_URL"):
    print(f"⚠️ Warning: .env not loaded from {env_path}")

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"DEBUG: URL loaded? {bool(SUPABASE_URL)}")
print(f"DEBUG: KEY loaded? {bool(SUPABASE_KEY)}")
if SUPABASE_KEY:
    print(f"DEBUG: KEY length: {len(SUPABASE_KEY)}")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def run_simulation():
    print("🎬 STARTING END-TO-END SIMULATION: The 'Sovereign' Flow")
    print("======================================================")
    
    # 1. User Visits Site & Selects Plan
    email = f"sim_user_{int(time.time())}@example.com"
    print(f"\n👤 1. USER: Visitor '{email}' selects 'Hvac Growth' plan.")
    
    # 2. Stripe Checkout (Mocked/Local)
    print(f"\n💳 2. BILLING: Generating Checkout Session...")
    try:
        # Using dummy price IDs for simulation if real ones fail locally
        url = billing.create_checkout_session(email, "price_mock_setup", "price_mock_sub")
        print(f"   ✅ Checkout URL Generated: {url[:30]}...")
    except Exception as e:
        print(f"   ⚠️ Billing Mock Note: Real Stripe call failed ({e}), proceeding with logic simulation.")

    # 3. Simulate Webhook (User Paid) -> Task Creation
    print(f"\n⚡ 3. WEBHOOK: Simulating 'checkout.session.completed' event...")
    
    # Manually insert provision task since we aren't actually paying in Stripe
    user_id = str(uuid.uuid4())
    task_payload = {
        "email": email,
        "stripe_customer_id": "cus_sim_" + user_id[:8],
        "subscription_id": "sub_sim_" + user_id[:8],
        "plan": "hvac_growth"
    }
    
    task_data = {
        "type": "provision_account",
        "payload": task_payload,
        "status": "pending",
        "priority": 10
    }
    
    try:
        res = supabase.table("tasks_queue").insert(task_data).execute()
        task_id = res.data[0]['id']
        print(f"   ✅ Task Created in Queue: {task_id} (Type: provision_account)")
    except Exception as e:
        print(f"   ❌ Failed to insert task: {e}")
        return

    # 4. Agent Act (Worker Pick Up)
    print(f"\n🤖 4. AGENT: Waiting for Worker to pick up task...")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        # Poll task status
        res = supabase.table("tasks_queue").select("*").eq("id", task_id).execute()
        if res.data:
            task = res.data[0]
            status = task['status']
            worker = task.get('worker_id', 'unknown')
            
            if status == 'processing':
                print(f"   🔄 Status: PROCESSING (Worker: {worker})")
            elif status == 'completed':
                print(f"   ✅ Status: COMPLETED! (Worker: {worker})")
                print(f"   🎉 SUCCESS: User provisioned, Agent activated.")
                return
            elif status == 'failed':
                print(f"   ❌ Status: FAILED. Check worker logs.")
                return
        
        time.sleep(2)
        print(".", end="", flush=True)

    print("\n\n⚠️ TIMEOUT: Worker did not complete task in 30s.")
    print("   (Is the 'sovereign_worker' running in the cloud? If not, run 'python worker.py' locally to test)")

if __name__ == "__main__":
    run_simulation()
