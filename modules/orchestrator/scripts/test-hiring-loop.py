import requests
import json
import time
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

# 1. Config
# DEFINITIVE URL WITH -afk SUFFIX
WEBHOOK_URL = "https://nearmiss1193-afk--ghl-omni-automation-ghl-webhook.modal.run"
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TEST_CONTACT_ID = f"test_candidate_{int(time.time())}"

def test_hiring_loop():
    print(f"Starting Loop Test for Contact: {TEST_CONTACT_ID}")

    # 2. Simulate Inbound Webhook
    payload = {
        "type": "InboundMessage",
        "contact_id": TEST_CONTACT_ID,
        "contact": {
            "tags": ["candidate", "hiring"],
            "name": "Test Candidate",
            "email": f"test_{int(time.time())}@candidate.com"
        },
        "message": {
            "body": "I'm interested in the Spartan AI role. I have experience with Agentic workflows."
        }
    }

    print(f"-> Sending simulated webhook to: {WEBHOOK_URL}")
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        print(f"-> Webhook Response Status: {response.status_code}")
        print(f"-> Webhook Body: {response.text}")
    except Exception as e:
        print(f"FAILED: Webhook Failed: {str(e)}")
        return

    # 3. Wait for database propagation
    print("-> Waiting 10 seconds for DB upsert...")
    time.sleep(10)

    # 4. Verify Database Entry
    print("-> Verifying Supabase 'hiring_pipeline' table...")
    try:
        res = supabase.table("hiring_pipeline").select("*").eq("ghl_contact_id", TEST_CONTACT_ID).execute()
        if len(res.data) > 0:
            print("SUCCESS: Candidate found in 'hiring_pipeline'!")
            print(f"Entry: {json.dumps(res.data[0], indent=2)}")
        else:
            print("FAILURE: Candidate NOT found in database.")
    except Exception as e:
        print(f"FAILED: DB Check Failed: {str(e)}")

if __name__ == "__main__":
    test_hiring_loop()
