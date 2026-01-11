"""
ENRICHED CAMPAIGN - Calls Decision Makers Directly
Uses Hunter.io + Apollo.io to find owner contact info before calling
"""
import os
import json
import requests
import re
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from enrich_decision_makers import enrich_lead

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = 'ee668638-38f0-4984-81ae-e2fd5d83084b'  # Twilio unlimited
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah
GHL_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(
    filename='enriched_campaign_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample leads for testing
TEST_LEADS = [
    {"company_name": "JW Plumbing Heating Air", "phone": "213-379-5931", "city": "Los Angeles", "state": "CA"},
    {"company_name": "Brody Pennell Heating AC", "phone": "310-810-2721", "city": "Los Angeles", "state": "CA"},
    {"company_name": "Gorgis AC Heating", "phone": "619-780-1104", "city": "San Diego", "state": "CA"},
    {"company_name": "San Diego Air Conditioning", "phone": "619-794-6867", "city": "San Diego", "state": "CA"},
    {"company_name": "Cabrillo Plumbing AC", "phone": "415-360-0560", "city": "San Francisco", "state": "CA"},
]

def normalize_phone(phone):
    return re.sub(r'\D', '', phone)[-10:]

def enrich_and_save(lead):
    """
    Enrich lead with decision maker contact info
    Returns enriched lead with owner name, email, phone
    """
    company = lead['company_name']
    
    print(f"\n🔍 Enriching: {company}")
    logger.info(f"ENRICH START: {company}")
    
    # Try to enrich
    enriched = enrich_lead(company)
    
    if enriched:
        # We found a decision maker!
        lead['owner_name'] = enriched.get('name')
        lead['owner_email'] = enriched.get('email')
        lead['owner_phone'] = enriched.get('phone')
        lead['owner_title'] = enriched.get('title')
        lead['enrichment_source'] = enriched.get('source')
        
        print(f"  ✅ Found: {enriched.get('name')} ({enriched.get('title')})")
        print(f"     Email: {enriched.get('email')}")
        print(f"     Phone: {enriched.get('phone')}")
        
        logger.info(f"ENRICH SUCCESS: {company} - {enriched.get('name')} - {enriched.get('source')}")
        
        return lead
    else:
        print(f"  ⚠️ No decision maker found - will use main line")
        logger.info(f"ENRICH FAILED: {company} - using main line")
        return lead

def make_call(lead):
    """Make call to decision maker if available, otherwise main line"""
    company = lead['company_name']
    
    # Prefer owner phone if available, otherwise use main line
    if lead.get('owner_phone'):
        phone = lead['owner_phone']
        contact_name = lead.get('owner_name', company)
        print(f"  📞 Calling OWNER: {contact_name} at {phone}")
    else:
        phone = f"+1{normalize_phone(lead['phone'])}"
        contact_name = company
        print(f"  📞 Calling MAIN LINE: {phone}")
    
    try:
        res = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": VAPI_PHONE_ID,
                "assistantId": ASSISTANT_ID,
                "customer": {"number": phone, "name": contact_name}
            },
            timeout=15
        )
        
        if res.status_code == 201:
            call_id = res.json().get('id', '')[:8]
            logger.info(f"CALL: {contact_name} - {call_id}")
            return True
    except Exception as e:
        logger.error(f"CALL FAILED: {company} - {e}")
        return False

def save_enriched_lead(lead):
    """Save enriched lead to Supabase"""
    email = lead.get('owner_email') or f"info@{re.sub(r'[^a-z0-9]', '', lead['company_name'].lower())}.com"
    
    try:
        supabase.table("leads").insert({
            'email': email,
            'status': 'contacted',
            'last_called': datetime.now().isoformat(),
            'agent_research': json.dumps({
                'company_name': lead['company_name'],
                'phone': lead.get('phone'),
                'city': lead.get('city'),
                'state': lead.get('state'),
                'owner_name': lead.get('owner_name'),
                'owner_email': lead.get('owner_email'),
                'owner_phone': lead.get('owner_phone'),
                'owner_title': lead.get('owner_title'),
                'enrichment_source': lead.get('enrichment_source'),
                'enriched_at': datetime.now().isoformat(),
                'industry': 'HVAC',
                'source': 'Enriched_Campaign',
            })
        }).execute()
        logger.info(f"SAVED: {lead['company_name']}")
        return True
    except:
        return False

def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      🎯 ENRICHED CAMPAIGN - DECISION MAKER DIRECT        ║
║      Using Hunter.io + Apollo.io for Owner Contacts      ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    logger.info(f"ENRICHED CAMPAIGN STARTED - {len(TEST_LEADS)} leads")
    
    for i, lead in enumerate(TEST_LEADS):
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(TEST_LEADS)}] {lead['company_name']}")
        print(f"{'='*60}")
        
        # Step 1: Enrich with decision maker info
        enriched_lead = enrich_and_save(lead)
        
        # Step 2: Save to database
        save_enriched_lead(enriched_lead)
        
        # Step 3: Make call (to owner if found, main line if not)
        make_call(enriched_lead)
        
        # Brief pause
        if i < len(TEST_LEADS) - 1:
            print(f"\n⏳ Next in 30 seconds...")
            time.sleep(30)
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      ✅ ENRICHED CAMPAIGN COMPLETE                       ║
║      Check logs for enrichment success rate              ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info("ENRICHED CAMPAIGN COMPLETE")

if __name__ == "__main__":
    main()
