import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

def run_test():
    # 1. Check Schema
    try:
        res = client.table('leads').select('*').limit(1).execute()
        if res.data:
            print(f"SCHEMA KEYS: {list(res.data[0].keys())}")
        else:
            print("NO DATA FOUND IN LEADS")
            return
    except Exception as e:
        print(f"SCHEMA CHECK ERROR: {e}")
        return

    # 2. Get 1 Fresh Lead
    try:
        res = client.table('leads').select('*').not_.is_('phone', 'null').eq('status', 'new').limit(1).execute()
        if not res.data:
            # Try any lead
            res = client.table('leads').select('*').not_.is_('phone', 'null').limit(1).execute()
        
        if res.data:
            lead = res.data[0]
            phone = lead['phone']
            print(f"TESTING LEAD: {lead['company_name']} ({phone})")
            
            # Update status ONLY first as a canary
            try:
                client.table('leads').update({"status": "contacted"}).eq("id", lead['id']).execute()
                print("UPDATE STATUS: SUCCESS")
            except Exception as e:
                print(f"UPDATE STATUS: FAILED - {e}")
                
            # Trigger Call
            try:
                resp = requests.post(
                    "https://api.vapi.ai/call",
                    headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
                    json={
                        "type": "outboundPhoneCall",
                        "phoneNumberId": VAPI_PHONE_ID,
                        "assistantId": SARAH_ID,
                        "customer": {"number": phone, "name": lead['company_name']}
                    },
                    timeout=10
                )
                print(f"VAPI CALL: {resp.status_code}")
            except Exception as e:
                print(f"VAPI CALL: ERROR - {e}")
        else:
            print("NO LEADS WITH PHONES FOUND")
    except Exception as e:
        print(f"LEAD TEST ERROR: {e}")

if __name__ == "__main__":
    run_test()
