import os
import time
import requests
import re
import json
import random
from datetime import datetime
import pytz
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# --- CONFIGURATION (ALF EDITION) ---
# Target: Senior Living Facilities
# Goal: Build Referral Network / inventory vacancies
TARGET_NICHE = "Assisted Living Facility"
TARGET_CITY = "Tampa" # Florida for high referral fees
TARGET_STATE = "FL"
BLITZ_LIMIT = 50 

# Load Environment Variables
load_dotenv()
GROK_API_KEY = os.getenv('GROK_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = "4e38087a-0937-4997-bc1c-4ddf77c5cf70" # Riley's Designated Line
ASSISTANT_ID = "93f64b69-314c-4040-b8d2-1c9f9a71dfc8" # Riley (ALF Specialist) - Auto-Created

if not all([GROK_API_KEY, SUPABASE_URL, SUPABASE_KEY, VAPI_PRIVATE_KEY, VAPI_PHONE_ID]):
    print("❌ Missing credentials")
    print(f"GROK: {bool(GROK_API_KEY)}")
    print(f"SUPA_URL: {bool(SUPABASE_URL)}")
    print(f"SUPA_KEY: {bool(SUPABASE_KEY)}")
    print(f"VAPI_KEY: {bool(VAPI_PRIVATE_KEY)}")
    print(f"PHONE_ID: {bool(VAPI_PHONE_ID)}")
    exit(1)

# Initialize Clients
genai.configure(api_key=GROK_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def log_error(company, phone, error_data):
    """Log Vapi errors to a comprehensive log file"""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] Error calling {company} ({phone}): {json.dumps(error_data)}\n"
    with open("alf_error.log", "a", encoding='utf-8') as f:
        f.write(log_entry)

def is_within_calling_hours():
    """Ensure we call FL leads during FL daytime (9am - 6pm ET)"""
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    return 9 <= now.hour < 18

def generate_leads(niche, city, state):
    print(f"🤖 Mining {niche} leads in {city}, {state}...")
    
    prompt = f"""
    Generate a JSON list of 5 REAL, OPERATING {niche} businesses in {city}, {state}.
    FOCUS: Independent Living, Assisted Living, Memory Care.
    CRITICAL: 
    1. Do NOT use '555' numbers. 
    2. Do NOT use major chains (Brookdale, etc) if possible, focus on local residential care homes.
    3. Return ONLY raw JSON. No markdown.
    
    Format:
    [
        {{"business_name": "Sunset Care Home", "phone": "+18135550199", "reason": "High ratings"}}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean markdown if present
        if text.startswith("```json"):
            text = text[7:-3]
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ Mining error: {e}")
        return []

def initiate_call(name, phone):
    print(f"📞 Calling {name} at {phone}...")
    
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumberId": VAPI_PHONE_ID,
        "customer": {
            "number": phone,
            "name": name[:40] # Truncate to avoid Vapi 400 error
        }
    }
    
    try:
        response = requests.post("https://api.vapi.ai/call", json=payload, headers=headers)
        
        if response.status_code == 201:
            print("✅ Call Initiated!")
            return True
        else:
            print(f"❌ Call Failed: {response.text}")
            try:
                error_data = response.json()
            except:
                error_data = {"text": response.text}
            log_error(name, phone, error_data)
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def main():
    print("🌅 ALF OUTREACH STARTED 🌅")
    print(f"Targeting: {TARGET_NICHE} in {TARGET_CITY}, {TARGET_STATE}")
    print(f"Agent: Riley ({ASSISTANT_ID})")

    total_calls = 0 # Initialize counter
    
    while True:
        if not is_within_calling_hours():
            print("zzz... Outside calling hours (9am-6pm ET). Sleeping 15m.")
            time.sleep(900)
            continue
            
        leads = generate_leads(TARGET_NICHE, TARGET_CITY, TARGET_STATE)
        
        if not leads:
            print("⚠️ No leads found. Retrying in 60s...")
            time.sleep(60)
            continue
            
        for lead in leads:
            if total_calls >= BLITZ_LIMIT:
                print("🛑 Daily Limit Reached.")
                return

            name = lead.get('business_name', 'Unknown')
            phone = lead.get('phone', '')
            
            # Simple validation
            if "555" in phone:
                print(f"⏭️ Skipping fake number: {phone}")
                continue
                
            success = initiate_call(name, phone)
            
            if success:
                total_calls += 1
                # Save to DB
                try:
                    supabase.table('leads_senior_living').insert({
                        "business_name": name,
                        "phone": phone,
                        "status": "called",
                        "city": TARGET_CITY,
                        "state": TARGET_STATE
                    }).execute()
                except Exception as db_err:
                    print(f"⚠️ DB Save Error: {db_err}")
            
            # Respect rate limits
            time.sleep(10)
            
        print("🔄 Batch complete. Analyzing results...")
        time.sleep(30)

if __name__ == "__main__":
    main()
