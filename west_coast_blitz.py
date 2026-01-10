"""
WEST COAST BLITZ - TURBO MODE
=============================
Target: Los Angeles, CA (Pacific Time)
Goal: Generate valid leads -> Call immediately -> Repeat until cutoff.
"""
import os
import json
import requests
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# CONFIG
TARGET_CITY = "Los Angeles"
TARGET_STATE = "CA"
GROK_API_KEY = os.getenv('GROK_API_KEY')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = os.getenv('VAPI_PHONE_NUMBER_ID')
ASSISTANT_ID = "1a797f12-e516-4fe8-a3a6-72f0cbf4a48d"

if not all([GROK_API_KEY, SUPABASE_URL, SUPABASE_KEY, VAPI_PRIVATE_KEY, VAPI_PHONE_ID]):
    print("❌ Missing credentials")
    exit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)

import google.generativeai as genai

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("❌ Missing GEMINI_API_KEY")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def generate_leads():
    print(f"\n[BLITZ] Hunting in {TARGET_CITY} (Gemini)...")
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
    Act as a lead generation expert. Find 5 REAL **HVAC** companies in {TARGET_CITY}, {TARGET_STATE}.
    
    CRITICAL RULES:
    1. DO NOT use fictional numbers (555-xxxx).
    2. Provide REAL public phone numbers (area codes 213, 310, 323, 424, 626, 818).
    3. NO TEXAS (TX) companies.
    4. Return valid JSON only.
    
    JSON Format:
    [
        {{
            "company_name": "Name",
            "owner_name": "Manager Name",
            "phone": "3105551234",
            "email": "email@domain.com",
            "industry": "HVAC"
        }}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"Gen error: {e}")
    return []

def call_lead(lead):
    phone = lead.get('phone', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    # STRICT VALIDATION
    if '555' in phone:
        print(f"🚫 REJECTED: 555 number ({phone})")
        return False
    if len(phone) < 10:
        print(f"🚫 REJECTED: Invalid length ({phone})")
        return False
        
    # Format E.164
    if not phone.startswith('+'):
        phone = f"+1{phone[-10:]}"
        
    print(f"📞 Calling {lead['company_name']} ({phone})...")
    
    try:
        res = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": VAPI_PHONE_ID,
                "assistantId": ASSISTANT_ID,
                "customer": {
                    "number": phone, 
                    "name": lead['company_name']
                }
            }
        )
        
        if res.status_code == 201:
            print(f"✅ CALL INITIATED: {res.json().get('id')}")
            # Save to DB
            lead['status'] = 'called'
            lead['city'] = TARGET_CITY
            lead['last_called'] = datetime.now().isoformat()
            lead['agent_research'] = json.dumps(lead)
            client.table("leads").insert(lead).execute()
            return True
        else:
            print(f"❌ Call Failed: {res.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    return False

def main():
    print("⚡ WEST COAST BLITZ STARTED ⚡")
    print(f"Target: {TARGET_CITY} (PT Timezone)")
    
    total_calls = 0
    
    while True:
        # Stop at 8:55 PM ET (5:55 PM PT)
        if datetime.now().hour >= 21: # 9 PM ET
             print("🛑 Cutoff reached (9 PM ET). Stopping.")
             break
             
        leads = generate_leads()
        if not leads:
            print("No leads found. Retrying...")
            time.sleep(5)
            continue
            
        print(f"Found {len(leads)} candidates.")
        
        for lead in leads:
            if call_lead(lead):
                total_calls += 1
                time.sleep(10) # 10s delay between calls
                
        print(f"Total Calls: {total_calls}")
        if total_calls >= 10: # Safety break
            print("Batch complete.")
            break 
            
    print("⚡ BLITZ COMPLETE ⚡")

if __name__ == "__main__":
    main()
