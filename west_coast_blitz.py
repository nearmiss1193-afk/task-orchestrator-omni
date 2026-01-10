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
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a" # Verified ID for 'Sarah (Temporarily John)'

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

def generate_leads(city, state):
    print(f"\n[BLITZ] Hunting in {city}, {state} (Gemini)...")
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
    Act as a lead generation expert. Find 5 REAL **HVAC** companies in {city}, {state}.
    
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
            # Log error to file for debugging
            with open("blitz_error.log", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] Error calling {lead['company_name']} ({phone}): {res.text}\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    return False

def main():
    print("⚡ MULTI-ZONE BLITZ STARTED ⚡")
    print("Strategy: CA until 10PM ET (7PM PT) -> Then HI/AK")

    total_calls = 0

    while True:
        current_hour = datetime.now().hour
        
        # TIMEZONE LOGIC (ET Based)
        # CA: Stop at 22:00 ET (7 PM PT)
        # HI: Stop at 01:00 ET (7 PM HST) - ample buffer
        
        target_city = "Honolulu"
        target_state = "HI"
        
        if current_hour < 22: # Before 10 PM ET
            target_city = "Los Angeles"
            target_state = "CA"
            cutoff_hour = 22
        elif current_hour < 24: # Before Midnight ET
            target_city = "Honolulu"
            target_state = "HI" 
            cutoff_hour = 1 # 1 AM next day
        else: # Late night fallback
            print("🛑 Global Safety Cutoff. Stopping.")
            break
            
        print(f"\n[BLITZ] Clock: {datetime.now().strftime('%H:%M')} ET | Target: {target_city}, {target_state}")
        
        leads = generate_leads(target_city, target_state) # Updated signature
        if not leads:
            print("No leads found. Retrying...")
            time.sleep(5)
            continue
            
        print(f"Found {len(leads)} candidates in {target_state}.")
        
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
