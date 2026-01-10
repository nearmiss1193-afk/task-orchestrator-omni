"""
EAST COAST BLITZ - IRONCLAD REST MODE (GEMINI 1.5)
==================================================
Target: Tampa, FL (Eastern Time)
Goal: Immediate Revenue Generation via Raw REST API.
"""
import os
import json
import requests
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import sys
import io

# FORCE UTF-8 for Windows Consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

# CONFIG
TARGET_CITY = "Tampa"
TARGET_STATE = "FL"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = os.getenv('VAPI_PHONE_NUMBER_ID') # Corrected Env Var
# Verified Assistant ID (Antigravity/Sarah)
ASSISTANT_ID = "a3e439a2-4560-4625-99c8-222678bf130d" 

if not all([GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY, VAPI_PRIVATE_KEY, VAPI_PHONE_ID]):
    print(f"❌ Missing credentials: Key={bool(VAPI_PRIVATE_KEY)}, PhoneID={bool(VAPI_PHONE_ID)}")
    exit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)

import logging

# Configure File Logging for Sentinel
logging.basicConfig(filename='campaign_logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_leads_rest(city, state):
    print(f"\n[BLITZ] Hunting in {city}, {state} (Gemini REST)...")
    logging.info(f"Generating leads for {city}")
    
    # Switch to 2.0-flash-exp (Known available, just rate limited)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Act as a lead generation expert. Find 5 REAL **HVAC** companies in {city}, {state}.
    
    CRITICAL RULES:
    1. DO NOT use fictional numbers (555-xxxx).
    2. Provide REAL public phone numbers (Area Code 813, 727, 352).
    3. Return valid JSON only.
    
    JSON Format:
    [
        {{
            "company_name": "Name",
            "phone": "8135551234"
        }}
    ]
    """
    
    # HARDCODED BACKUP CACHE (To bypass 429s)
    # Using TEST_PHONE to verify system operation
    test_phone = os.getenv('TEST_PHONE', '813-555-0101') 
    
    backup_leads = [
        {"company_name": "Test Protocol Alpha", "phone": test_phone},
        {"company_name": "Test Protocol Beta", "phone": test_phone}
    ]
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code == 429:
            print("⏳ 429 Quota Exceeded. Using BACKUP CACHE...")
            logging.warning("429 Quota Exceeded. Using Backup Cache.")
            time.sleep(5)
            # Failover to backup
            return backup_leads
            
        response.raise_for_status()
        data = response.json()
        
        # Extract text from complex Gemini response structure
        try:
            content = data['candidates'][0]['content']['parts'][0]['text']
        except KeyError:
            print(f"⚠️ Unexpected JSON structure: {data}")
            return []

        # Extract JSON from Markdown
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            print(f"⚠️ Could not parse JSON from Gemini: {content[:100]}...")
            return []
            
    except Exception as e:
        print(f"❌ REST Generation Error: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
             print(f"Response: {response.text}")
        return []

def push_to_ghl(lead):
    phone = lead.get('phone', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    # Format E.164 (GHL prefers this)
    if not phone.startswith('+'):
        phone = f"+1{phone[-10:]}"
        
    print(f"🚀 Pushing {lead['company_name']} ({phone}) to GHL...")
    logging.info(f"Pushing {lead['company_name']} to GHL...")
    
    webhook_url = os.getenv('GHL_SMS_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ GHL_SMS_WEBHOOK_URL missing in .env")
        logging.error("GHL_SMS_WEBHOOK_URL missing")
        return False
        
    payload = {
        "name": lead['company_name'],
        "phone": phone,
        "email": f"info@{lead['company_name'].replace(' ', '').lower()}.com", # Best guess email
        "source": "Empire_Blitz_AI",
        "tags": ["trigger-vortex"] # Triggers Spartan Workflow
    }
    
    try:
        res = requests.post(webhook_url, json=payload)
        
        logging.info(f"GHL Response Code: {res.status_code}")
        
        if res.status_code == 200 or res.status_code == 201:
            print(f"✅ GHL ACCEPTED: {lead['company_name']}")
            logging.info(f"✅ GHL ACCEPTED: {lead['company_name']}")
            
            # Save to DB
            try:
                # Create a clean copy for DB insertion
                db_record = {
                    'company_name': lead.get('company_name'),
                    'phone': lead.get('phone'),
                    'city': TARGET_CITY,
                    'status': 'pushed_to_ghl',
                    'last_called': datetime.now().isoformat(),
                    'agent_research': json.dumps(lead) # Store full raw lead data here
                }
                client.table("leads").insert(db_record).execute()
            except Exception as db_err:
                print(f"⚠️ DB Error: {db_err}")
                logging.error(f"DB Error: {db_err}")
            return True
        else:
            print(f"❌ GHL Rejected: {res.text}")
            logging.error(f"❌ GHL Rejected: {res.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"❌ Exception in push_to_ghl: {e}")
    return False

def main():
    print(f"⚡ EAST COAST BLITZ STARTED (Target: {TARGET_CITY}) ⚡")
    print("Using Engine: Gemini 1.5 Flash (Direct REST)")
    
    total_calls = 0
    while True:
        # Generate Batch
        leads = generate_leads_rest(TARGET_CITY, TARGET_STATE)
        
        if not leads:
            print("No leads found. Retrying in 10s...")
            time.sleep(10)
            continue
            
        print(f"🎯 Candidates found: {len(leads)}")
        
        for lead in leads:
            if push_to_ghl(lead):
                total_calls += 1
                print("⏳ Cooldown: 15s...")
                time.sleep(15)
                
        if total_calls >= 5:
            print("🛑 Target Reached (5 Calls). Pausing for user review.")
            break
            
        print("🔄 Batch Complete. Rescanning...")
        time.sleep(5)

if __name__ == "__main__":
    main()
