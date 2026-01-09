# launch_roofing_campaign.py - Roofing-specific drip campaign with John (male AI)
"""
A/B Test Setup:
- HVAC leads → Sarah (female, warm)
- Roofing leads → John (male, direct/contractor)
- Same infrastructure, different personas
"""
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import pytz

load_dotenv()

# Config
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")

# John's IDs
JOHN_ASSISTANT_ID = "78b4c14a-b44a-4096-82f5-a10106d1bfd2"
ROOFING_PHONE_ID = "40379c46-4b27-45de-8294-4908b694dfc6"  # 2nd line: +1 863-692-8548

# Initialize
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_lead_timezone(state):
    """Map state to timezone."""
    mapping = {
        'FL': 'US/Eastern', 'GA': 'US/Eastern', 'NC': 'US/Eastern',
        'TX': 'US/Central', 'IL': 'US/Central', 'LA': 'US/Central',
        'AZ': 'US/Mountain', 'CO': 'US/Mountain', 'NM': 'US/Mountain',
        'CA': 'US/Pacific', 'WA': 'US/Pacific', 'OR': 'US/Pacific'
    }
    return mapping.get(state, 'US/Eastern')

def is_within_window(tz_name):
    """Check if current time is between 07:00 and 19:00 local."""
    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        return 7 <= now.hour < 19
    except:
        return True

def make_call(phone, first_name, company_name):
    """Initiate call via Vapi with John."""
    url = "https://api.vapi.ai/call"
    headers = {
        "Authorization": f"Bearer {VAPI_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "assistantId": JOHN_ASSISTANT_ID,
        "phoneNumberId": ROOFING_PHONE_ID,
        "customer": {
            "number": phone,
            "name": first_name
        },
        "assistantOverrides": {
            "variableValues": {
                "customer_name": first_name,
                "company_name": company_name
            }
        }
    }
    
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code == 201, res.json() if res.status_code == 201 else res.text

def run_roofing_drip():
    """Main drip loop for roofing leads only."""
    print("=" * 50)
    print("ROOFING CAMPAIGN - JOHN (Male AI)")
    print(f"Assistant: {JOHN_ASSISTANT_ID}")
    print(f"Phone: {ROOFING_PHONE_ID}")
    print("=" * 50)
    
    while True:
        try:
            # Fetch roofing leads only
            result = supabase.table('leads').select('*').eq('status', 'ready_to_send').execute()
            
            roofing_leads = [
                lead for lead in result.data 
                if lead.get('agent_research', {}).get('industry') == 'Roofing'
            ]
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Roofing leads ready: {len(roofing_leads)}")
            
            for lead in roofing_leads:
                research = lead.get('agent_research', {})
                state = research.get('state', 'FL')
                tz_name = get_lead_timezone(state)
                
                # Check timezone window
                if not is_within_window(tz_name):
                    print(f"  [SKIP] {lead.get('company_name')} - Outside 7AM-7PM for {state}")
                    continue
                
                phone = research.get('phone')
                if not phone:
                    continue
                
                # Format phone
                phone_clean = ''.join(filter(str.isdigit, phone))
                if len(phone_clean) == 10:
                    phone_clean = '+1' + phone_clean
                elif len(phone_clean) == 11 and phone_clean[0] == '1':
                    phone_clean = '+' + phone_clean
                
                first_name = research.get('first_name', 'there')
                company = lead.get('company_name', 'your company')
                
                print(f"\n  [CALL] John -> {company} ({state})")
                print(f"         Phone: {phone_clean}")
                
                success, response = make_call(phone_clean, first_name, company)
                
                if success:
                    print(f"         [OK] Call initiated")
                    # Update status
                    supabase.table('leads').update({
                        'status': 'contacted',
                        'last_contact': datetime.utcnow().isoformat()
                    }).eq('id', lead['id']).execute()
                else:
                    print(f"         [FAIL] {response}")
                
                # Pace: 10 min between calls
                print("         Waiting 10 minutes...")
                time.sleep(600)
            
            # Sleep between cycles
            print("\n  [CYCLE] Waiting 5 minutes for next batch...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n[STOP] Campaign stopped by user")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_roofing_drip()
