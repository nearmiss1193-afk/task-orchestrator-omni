import os
import requests
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a" # Sarah 3.0

def force_contact():
    # Get leads with phone numbers that haven't been contacted
    res = client.table('leads').select('*').not_.is_('phone', 'null').is_('last_called', 'null').limit(3).execute()
    
    if not res.data:
        print("No fresh leads with phones found.")
        return

    for lead in res.data:
        phone = lead['phone']
        company = lead['company_name']
        print(f"Force contacting: {company} @ {phone}")
        
        # Call via Vapi
        try:
            resp = requests.post(
                "https://api.vapi.ai/call",
                headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
                json={
                    "type": "outboundPhoneCall",
                    "phoneNumberId": VAPI_PHONE_ID,
                    "assistantId": SARAH_ID,
                    "customer": {"number": phone, "name": company}
                },
                timeout=15
            )
            print(f"Vapi Call Status: {resp.status_code}")
        except Exception as e:
            print(f"Vapi Call Error: {e}")
        
        # Mark as contacted
        now = datetime.now().isoformat()
        try:
            # Try updating status and last_called first
            client.table('leads').update({
                "status": "contacted", 
                "last_called": now
            }).eq("id", lead['id']).execute()
            print("       Lead updated (status, last_called)")
            
            # Try last_contact_at separately if it failed before
            try:
                client.table('leads').update({
                    "last_contact_at": now
                }).eq("id", lead['id']).execute()
                print("       Lead updated (last_contact_at)")
            except Exception as e:
                print(f"       Failed to update last_contact_at: {e}")
                
        except Exception as e:
            print(f"       Failed to update lead status: {e}")

if __name__ == "__main__":
    force_contact()
