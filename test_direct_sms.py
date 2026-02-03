
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_direct_sms():
    hook_url = "https://services.leadconnectorhq.com/hooks/M7YwDClf34RsNhPQfhS7/webhook-trigger/4d138ed0-d86e-49f2-b214-3f44e2657285"
    # Actually, I should use the one from the deploy.py environment
    # GHL_SMS_WEBHOOK_URL="https://services.leadconnectorhq.com/hooks/uFYcZA7Zk6EcBze5B4oH/webhook-trigger/6d6c2999-563b-483a-8610-863a39e801b7"
    
    # MISSION: GHOST EXORCISM - DIRECT PROOF
    url = "https://services.leadconnectorhq.com/hooks/uFYcZA7Zk6EcBze5B4oH/webhook-trigger/6d6c2999-563b-483a-8610-863a39e801b7"
    
    payload = {
        "phone": "+13529368152",
        "message": "⚫ TRUTH-BASE-0 VERIFICATION: Sovereign Engine is re-initializing. This is a direct engine bypass test. Reply if received.",
        "contact_id": "c086f2ce-72f5-4f9f-b414-e0432908c6bc" # Your GHL ID
    }
    
    print(f"📡 SENDING DIRECT SMS TO {payload['phone']}...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"✅ STATUS: {response.status_code}")
        print(f"✅ RESPONSE: {response.text}")
    except Exception as e:
        print(f"❌ FAIL: {e}")

if __name__ == "__main__":
    test_direct_sms()
