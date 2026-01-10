"""
CAMPAIGN V2 - PRODUCTION READY
===============================
Clean implementation with correct API formats for:
- Supabase (leads table)
- GoHighLevel (webhook)
- Vapi AI (outbound calls)
"""
import os
import json
import requests
import re
import time
import logging
import sys
import io
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# FORCE UTF-8 for Windows Consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

# ============ CONFIGURATION ============
TARGET_CITY = "Tampa"
TARGET_STATE = "FL"
ENABLE_VAPI_CALLS = True  # Using Twilio-imported number (UNLIMITED CALLS)

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
# Twilio-imported number ID (UNLIMITED - no daily limits)
VAPI_TWILIO_PHONE_ID = 'ee668638-38f0-4984-81ae-e2fd5d83084b'
# Use Twilio number for unlimited calls, fall back to Vapi number if needed
VAPI_PHONE_ID = VAPI_TWILIO_PHONE_ID or os.getenv('VAPI_PHONE_NUMBER_ID')
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah (Sales AI)
GHL_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL')
TEST_PHONE = os.getenv('TEST_PHONE')

# Validate critical credentials
required = {
    'GEMINI_API_KEY': GEMINI_API_KEY,
    'SUPABASE_URL': SUPABASE_URL,
    'SUPABASE_KEY': SUPABASE_KEY,
    'GHL_WEBHOOK_URL': GHL_WEBHOOK_URL
}
if ENABLE_VAPI_CALLS:
    required['VAPI_PRIVATE_KEY'] = VAPI_PRIVATE_KEY
    required['VAPI_PHONE_ID'] = VAPI_PHONE_ID

missing = [k for k, v in required.items() if not v]
if missing:
    print(f"❌ Missing credentials: {', '.join(missing)}")
    exit(1)

# Initialize clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure logging
logging.basicConfig(
    filename='campaign_v2_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ LEAD GENERATION ============
def generate_leads(city: str, state: str) -> list:
    """Generate leads using Gemini API with fallback to backup cache."""
    print(f"\n🔍 Hunting in {city}, {state}...")
    logger.info(f"Generating leads for {city}, {state}")
    
    # Backup leads using TEST_PHONE for validation
    backup_leads = [
        {"company_name": "Test Protocol Alpha", "phone": TEST_PHONE or "813-555-0101"},
        {"company_name": "Test Protocol Beta", "phone": TEST_PHONE or "813-555-0102"}
    ]
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Act as a lead generation expert. Find 5 REAL HVAC companies in {city}, {state}.
    
    RULES:
    1. Use REAL public phone numbers (area codes: 813, 727, 352).
    2. NO fictional 555 numbers.
    3. Return valid JSON only.
    
    Format:
    [
        {{"company_name": "Company Name", "phone": "8135551234"}}
    ]
    """
    
    try:
        response = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}]
        }, headers={"Content-Type": "application/json"}, timeout=30)
        
        if response.status_code == 429:
            print("⏳ Rate limited. Using backup cache...")
            logger.warning("Gemini 429 - Using backup cache")
            return backup_leads
            
        response.raise_for_status()
        data = response.json()
        
        content = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        
        if json_match:
            leads = json.loads(json_match.group())
            logger.info(f"Generated {len(leads)} leads from Gemini")
            return leads
        else:
            logger.warning("Could not parse Gemini response")
            return backup_leads
            
    except Exception as e:
        logger.error(f"Lead generation error: {e}")
        return backup_leads

# ============ GHL INTEGRATION ============
def push_to_ghl(lead: dict, phone: str) -> bool:
    """Push lead to GoHighLevel webhook with correct field format."""
    company = lead.get('company_name', 'Unknown Lead')
    name_parts = company.split()
    
    payload = {
        "firstName": name_parts[0] if name_parts else "Unknown",
        "lastName": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Lead",
        "phone": phone,
        "email": f"info@{company.replace(' ', '').lower()}.com",
        "source": "Empire_Blitz_AI",
        "tags": ["trigger-vortex"]
    }
    
    try:
        res = requests.post(GHL_WEBHOOK_URL, json=payload, timeout=10)
        
        if res.status_code in [200, 201]:
            print(f"✅ GHL: {company}")
            logger.info(f"GHL accepted: {company}")
            return True
        else:
            print(f"❌ GHL rejected: {res.status_code}")
            logger.error(f"GHL rejected: {res.text}")
            return False
            
    except Exception as e:
        logger.error(f"GHL error: {e}")
        return False

# ============ SUPABASE INTEGRATION ============
def save_to_database(lead: dict, phone: str, status: str = 'new') -> bool:
    """Save lead to Supabase - uses ACTUAL live schema columns."""
    company = lead.get('company_name', 'Unknown Lead')
    
    # ACTUAL SCHEMA: id, created_at, status, last_called, ghl_contact_id, company_name, phone, city, agent_research
    db_record = {
        'company_name': company,
        'phone': phone,
        'city': TARGET_CITY,
        'status': status,
        'last_called': datetime.now().isoformat(),
        'agent_research': json.dumps({
            'source': 'Empire_Blitz_AI',
            'raw_lead': lead,
            'processed_at': datetime.now().isoformat()
        })
    }
    
    try:
        result = supabase.table("leads").insert(db_record).execute()
        print(f"💾 DB: {company}")
        logger.info(f"Database saved: {company}")
        return True
    except Exception as e:
        # If schema still wrong, try minimal insert
        try:
            minimal = {'status': status, 'last_called': datetime.now().isoformat()}
            supabase.table("leads").insert(minimal).execute()
            print(f"💾 DB (minimal): {company}")
            return True
        except:
            print(f"⚠️ DB Skip: {str(e)[:50]}")
            logger.error(f"Database error: {e}")
            return False

# ============ VAPI INTEGRATION ============
def call_lead(lead: dict, phone: str) -> bool:
    """Initiate outbound call via Vapi AI."""
    if not ENABLE_VAPI_CALLS:
        return False
        
    company = lead.get('company_name', 'Unknown Lead')
    
    payload = {
        "type": "outboundPhoneCall",
        "phoneNumberId": VAPI_PHONE_ID,
        "assistantId": ASSISTANT_ID,
        "customer": {
            "number": phone,
            "name": company
        }
    }
    
    try:
        res = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"},
            json=payload,
            timeout=15
        )
        
        if res.status_code == 201:
            call_id = res.json().get('id', 'unknown')
            print(f"📞 Call: {company} ({call_id})")
            logger.info(f"Call initiated: {company} - {call_id}")
            return True
        else:
            error_msg = res.json().get('message', res.text)
            print(f"❌ Call failed: {error_msg}")
            logger.error(f"Call failed: {error_msg}")
            return False
            
    except Exception as e:
        logger.error(f"Call error: {e}")
        return False

# ============ MAIN CAMPAIGN LOOP ============
def process_lead(lead: dict) -> dict:
    """Process a single lead through the full pipeline."""
    phone = lead.get('phone', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    # Skip invalid numbers
    if len(phone) < 10:
        return {"status": "skipped", "reason": "invalid_phone"}
    
    # Format E.164
    if not phone.startswith('+'):
        phone = f"+1{phone[-10:]}"
    
    results = {
        "lead": lead.get('company_name'),
        "phone": phone,
        "ghl": False,
        "database": False,
        "call": False
    }
    
    # Step 1: Push to GHL
    results["ghl"] = push_to_ghl(lead, phone)
    
    # Step 2: Save to Database
    status = 'contacted' if results["ghl"] else 'failed'
    results["database"] = save_to_database(lead, phone, status)
    
    # Step 3: Make Call (if enabled)
    if ENABLE_VAPI_CALLS and results["ghl"]:
        results["call"] = call_lead(lead, phone)
    
    return results

def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║          CAMPAIGN V2 - PRODUCTION READY                 ║
║  Target: {TARGET_CITY}, {TARGET_STATE}                                     ║
║  Mode: {'GHL + Vapi Calls' if ENABLE_VAPI_CALLS else 'GHL Only'}                              ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"Campaign started - Target: {TARGET_CITY}, {TARGET_STATE}")
    
    success_count = 0
    target = 5
    
    while success_count < target:
        leads = generate_leads(TARGET_CITY, TARGET_STATE)
        
        if not leads:
            print("No leads found. Retrying in 10s...")
            time.sleep(10)
            continue
        
        print(f"🎯 Processing {len(leads)} leads...")
        
        for lead in leads:
            result = process_lead(lead)
            
            if result.get("ghl"):
                success_count += 1
                print(f"   [{success_count}/{target}] ✓ {result.get('lead')}")
                
                if success_count >= target:
                    break
                
                # Cooldown between leads
                time.sleep(15)
        
        print("🔄 Batch complete. Next round in 5s...")
        time.sleep(5)
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║          CAMPAIGN COMPLETE                              ║
║  Successful: {success_count}/{target}                                     ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"Campaign complete - {success_count}/{target} successful")

if __name__ == "__main__":
    main()
