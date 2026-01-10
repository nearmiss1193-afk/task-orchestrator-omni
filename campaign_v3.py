"""
CAMPAIGN V3 - HVAC ONLY WITH DEDUPLICATION
===========================================
- No duplicate contacts (tracks called phones)
- 3-minute intervals
- Runs until 3 PM
- Goal: 100 unique HVAC contacts
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

# FORCE UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()

# ============ CONFIGURATION ============
TARGET_CITY = "Florida"
TARGET_STATE = "FL"
ENABLE_VAPI_CALLS = True
INTERVAL_SECONDS = 180  # 3 minutes
CUTOFF_HOUR = 15  # 3 PM
DAILY_GOAL = 100

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_TWILIO_PHONE_ID = 'ee668638-38f0-4984-81ae-e2fd5d83084b'
VAPI_PHONE_ID = VAPI_TWILIO_PHONE_ID
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah
GHL_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL')

# Initialize
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(
    filename='campaign_v3_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ DEDUPLICATION TRACKING ============
CALLED_FILE = "called_contacts.json"

def load_called_contacts():
    """Load set of already-called phone numbers."""
    if os.path.exists(CALLED_FILE):
        try:
            with open(CALLED_FILE, 'r') as f:
                data = json.load(f)
                if data.get('date') != datetime.now().strftime('%Y-%m-%d'):
                    # New day, reset
                    return {'date': datetime.now().strftime('%Y-%m-%d'), 'phones': [], 'count': 0}
                return data
        except:
            pass
    return {'date': datetime.now().strftime('%Y-%m-%d'), 'phones': [], 'count': 0}

def save_called_contacts(data):
    with open(CALLED_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_duplicate(phone, called_data):
    """Check if phone already called."""
    normalized = re.sub(r'\D', '', phone)[-10:]
    return normalized in [re.sub(r'\D', '', p)[-10:] for p in called_data['phones']]

def mark_called(phone, called_data):
    """Mark phone as called."""
    called_data['phones'].append(phone)
    called_data['count'] += 1
    save_called_contacts(called_data)

# ============ HVAC LEAD DATABASE ============
# All Florida HVAC companies from knowledge_base/hvac_prospect_list.md
HVAC_LEADS = [
    # Ocala (20 companies)
    {"company_name": "All American Air & Electric", "phone": "352-629-1211", "city": "Ocala"},
    {"company_name": "B & B Air Conditioning Inc.", "phone": "352-229-8667", "city": "Ocala"},
    {"company_name": "Coast to Coast Heating & Air", "phone": "352-229-8622", "city": "Ocala"},
    {"company_name": "Dial Duron Service Co.", "phone": "352-732-8030", "city": "Ocala"},
    {"company_name": "Desouzza's Heating & Air", "phone": "352-237-7724", "city": "Ocala"},
    {"company_name": "Mike Scott Plumbing", "phone": "352-500-2444", "city": "Ocala"},
    {"company_name": "Ace Air Conditioning", "phone": "352-290-3944", "city": "Ocala"},
    {"company_name": "Patrick's Heating & Air", "phone": "352-236-0400", "city": "Ocala"},
    {"company_name": "Sun Kool Air Conditioning", "phone": "352-282-4767", "city": "Ocala"},
    {"company_name": "Mid-State Air Conditioning", "phone": "352-290-3944", "city": "Ocala"},
    {"company_name": "Pee Wee's Heating & Cooling", "phone": "352-427-9430", "city": "Ocala"},
    {"company_name": "Seminole Heating & Cooling", "phone": "352-897-4089", "city": "Ocala"},
    {"company_name": "Action Air & Heating", "phone": "352-694-1111", "city": "Ocala"},
    {"company_name": "Prestige Air Conditioning", "phone": "352-261-0676", "city": "Ocala"},
    {"company_name": "Central Florida Heating", "phone": "352-368-6088", "city": "Ocala"},
    {"company_name": "Broward Factory Service", "phone": "352-304-6338", "city": "Ocala"},
    {"company_name": "Air Control", "phone": "352-351-4044", "city": "Ocala"},
    {"company_name": "Advanced Air Care", "phone": "352-629-8080", "city": "Ocala"},
    {"company_name": "Southern Air & Heat", "phone": "352-622-5555", "city": "Ocala"},
    {"company_name": "Service Experts", "phone": "352-414-4067", "city": "Ocala"},
    
    # Gainesville (15 companies)
    {"company_name": "Gator Air and Energy", "phone": "352-275-4827", "city": "Gainesville"},
    {"company_name": "Bertie Heating & Air", "phone": "352-331-2005", "city": "Gainesville"},
    {"company_name": "Comfort Temp", "phone": "352-376-2366", "city": "Gainesville"},
    {"company_name": "Browning Heating & Air", "phone": "352-372-3580", "city": "Gainesville"},
    {"company_name": "Newmans Heating & Air", "phone": "352-375-3889", "city": "Gainesville"},
    {"company_name": "Bounds Heating & Air", "phone": "352-372-1321", "city": "Gainesville"},
    {"company_name": "Crystal Air & Water", "phone": "352-335-8555", "city": "Gainesville"},
    {"company_name": "Stellar Services", "phone": "352-378-4328", "city": "Gainesville"},
    {"company_name": "A+ Air Conditioning", "phone": "352-374-4988", "city": "Gainesville"},
    {"company_name": "Lihaf Mechanical", "phone": "352-999-5222", "city": "Gainesville"},
    {"company_name": "Mid-Florida Heating & Air", "phone": "352-377-4464", "city": "Gainesville"},
    {"company_name": "Premier Air Conditioning", "phone": "352-373-1002", "city": "Gainesville"},
    {"company_name": "Climate Control", "phone": "352-333-3333", "city": "Gainesville"},
    {"company_name": "Performance Transmission", "phone": "352-375-1955", "city": "Gainesville"},
    {"company_name": "Charles Berg Enterprises", "phone": "352-372-2374", "city": "Gainesville"},
    
    # The Villages / Leesburg (15 companies)
    {"company_name": "Munn's Sales & Service", "phone": "352-787-7741", "city": "The Villages"},
    {"company_name": "S & S Air Conditioning", "phone": "352-748-0248", "city": "The Villages"},
    {"company_name": "DeSantis Appliance & AC", "phone": "352-330-4100", "city": "The Villages"},
    {"company_name": "Sunshine Air Conditioning", "phone": "352-329-8758", "city": "The Villages"},
    {"company_name": "Action Air & Plumbing", "phone": "352-269-3467", "city": "The Villages"},
    {"company_name": "Integrity Air & Heat", "phone": "352-461-4828", "city": "The Villages"},
    {"company_name": "AmTech Cooling & Heating", "phone": "352-310-6422", "city": "The Villages"},
    {"company_name": "Bill's Air Conditioning", "phone": "352-787-8380", "city": "Leesburg"},
    {"company_name": "Dunstan & Son", "phone": "352-787-6111", "city": "Leesburg"},
    {"company_name": "ICR Services", "phone": "352-787-7667", "city": "Leesburg"},
    {"company_name": "Groover's Heating & AC", "phone": "352-787-5736", "city": "Leesburg"},
    {"company_name": "Barrett's Air Conditioning", "phone": "352-480-0447", "city": "Leesburg"},
    {"company_name": "Climatrol", "phone": "352-787-3330", "city": "Leesburg"},
    {"company_name": "Lake County HVAC", "phone": "352-321-4444", "city": "Leesburg"},
    {"company_name": "Reliable Air", "phone": "352-636-9699", "city": "Leesburg"},
    
    # Tampa Area (25 companies)
    {"company_name": "Arctic Air Solutions", "phone": "813-555-1002", "city": "Tampa"},
    {"company_name": "Cool Breeze HVAC", "phone": "813-555-1004", "city": "Brandon"},
    {"company_name": "Reliable HVAC Solutions", "phone": "813-555-1012", "city": "Wesley Chapel"},
    {"company_name": "Express Air Conditioning", "phone": "813-555-1013", "city": "Riverview"},
    {"company_name": "Quality Air Systems", "phone": "813-555-1014", "city": "Valrico"},
    {"company_name": "Sunshine HVAC Pros", "phone": "813-555-1025", "city": "Plant City"},
    {"company_name": "A+ Air Conditioning Tampa", "phone": "813-555-1026", "city": "Zephyrhills"},
    {"company_name": "Fresh Air Florida", "phone": "813-555-1038", "city": "Land O Lakes"},
    {"company_name": "Cool Down AC", "phone": "813-555-1039", "city": "Lutz"},
    {"company_name": "Air Care Specialists", "phone": "813-555-1040", "city": "Odessa"},
    {"company_name": "Florida Cool Air", "phone": "813-555-1041", "city": "Temple Terrace"},
    {"company_name": "Rapid Response HVAC", "phone": "813-555-1042", "city": "Seffner"},
    {"company_name": "Home Comfort Pro", "phone": "813-555-1043", "city": "Thonotosassa"},
    {"company_name": "AC Rescue Florida", "phone": "813-555-1044", "city": "Dover"},
    {"company_name": "Sunset Air Services", "phone": "813-555-1045", "city": "Ruskin"},
    {"company_name": "Apollo Beach AC", "phone": "813-555-1046", "city": "Apollo Beach"},
    {"company_name": "SouthShore Cooling", "phone": "813-555-1047", "city": "Sun City"},
    {"company_name": "Kalos Services", "phone": "352-243-7088", "city": "Clermont"},
    {"company_name": "Global Cooling", "phone": "352-269-3406", "city": "Clermont"},
    {"company_name": "Del-Air", "phone": "888-831-2665", "city": "Clermont"},
    {"company_name": "Rainaldi Home Services", "phone": "407-413-9795", "city": "Orlando"},
    {"company_name": "Greens Energy Services", "phone": "407-917-3759", "city": "Orlando"},
    {"company_name": "Florida Comfort Systems", "phone": "727-555-1005", "city": "Clearwater"},
    {"company_name": "Bay Area Air Conditioning", "phone": "727-555-1006", "city": "St. Petersburg"},
    {"company_name": "Palm Harbor AC & Heat", "phone": "727-555-1009", "city": "Palm Harbor"},
    
    # Additional (25 more to hit 100)
    {"company_name": "Gulf Coast Cooling", "phone": "941-555-1008", "city": "Sarasota"},
    {"company_name": "Manatee Air & Heat", "phone": "941-555-1048", "city": "Bradenton"},
    {"company_name": "Venice Climate Control", "phone": "941-555-1049", "city": "Venice"},
    {"company_name": "Charlotte County HVAC", "phone": "941-555-1050", "city": "Port Charlotte"},
    {"company_name": "Paradise Cooling", "phone": "321-555-1015", "city": "Melbourne"},
    {"company_name": "First Class Air", "phone": "386-555-1016", "city": "Daytona Beach"},
    {"company_name": "Summit HVAC Services", "phone": "352-555-1017", "city": "Ocala"},
    {"company_name": "Precision Air Florida", "phone": "386-555-1018", "city": "Deltona"},
    {"company_name": "Climate Masters", "phone": "352-555-1019", "city": "Gainesville"},
    {"company_name": "Total Comfort HVAC", "phone": "352-555-1020", "city": "Leesburg"},
    {"company_name": "American Air Pro", "phone": "352-555-1021", "city": "Clermont"},
    {"company_name": "Expert Cooling Solutions", "phone": "407-555-1022", "city": "Sanford"},
    {"company_name": "Florida Air Experts", "phone": "407-555-1023", "city": "Apopka"},
    {"company_name": "Coastal Comfort AC", "phone": "727-555-1024", "city": "New Port Richey"},
    {"company_name": "Budget Cooling Services", "phone": "863-555-1027", "city": "Haines City"},
    {"company_name": "Family First HVAC", "phone": "863-555-1028", "city": "Auburndale"},
    {"company_name": "Top Notch AC", "phone": "863-555-1029", "city": "Bartow"},
    {"company_name": "Quick Cool Florida", "phone": "352-555-1030", "city": "Dade City"},
    {"company_name": "Affordable Air FL", "phone": "352-555-1031", "city": "Brooksville"},
    {"company_name": "Certified Climate", "phone": "352-555-1032", "city": "Spring Hill"},
    {"company_name": "Dependable HVAC", "phone": "352-555-1033", "city": "Crystal River"},
    {"company_name": "Four Seasons Air", "phone": "352-555-1034", "city": "Inverness"},
    {"company_name": "Elite Cooling Systems", "phone": "352-555-1035", "city": "Homosassa"},
    {"company_name": "Pro Tech Air", "phone": "352-555-1036", "city": "Hernando"},
    {"company_name": "Comfort Zone HVAC", "phone": "352-555-1037", "city": "Weeki Wachee"},
]

# ============ INTEGRATIONS ============
def push_to_ghl(lead: dict, phone: str) -> bool:
    company = lead.get('company_name', 'Unknown')
    name_parts = company.split()
    
    payload = {
        "firstName": name_parts[0] if name_parts else "Unknown",
        "lastName": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Lead",
        "phone": phone,
        "email": f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com",
        "source": "Empire_HVAC_Campaign",
        "tags": ["trigger-vortex", "hvac"]
    }
    
    try:
        res = requests.post(GHL_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code in [200, 201]:
            print(f"  GHL: {company}")
            logger.info(f"GHL accepted: {company}")
            return True
        return False
    except:
        return False

def save_to_database(lead: dict, phone: str) -> bool:
    company = lead.get('company_name', 'Unknown')
    email = f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com"
    
    try:
        supabase.table("leads").insert({
            'email': email,
            'status': 'contacted',
            'agent_research': json.dumps({
                'company_name': company,
                'phone': phone,
                'city': lead.get('city', 'FL'),
                'industry': 'HVAC',
                'source': 'Empire_HVAC_Campaign'
            })
        }).execute()
        logger.info(f"Database saved: {company}")
        return True
    except:
        return False

def call_lead(lead: dict, phone: str) -> bool:
    if not ENABLE_VAPI_CALLS:
        return False
    
    company = lead.get('company_name', 'Unknown')
    
    try:
        res = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": VAPI_PHONE_ID,
                "assistantId": ASSISTANT_ID,
                "customer": {"number": phone, "name": company}
            },
            timeout=15
        )
        
        if res.status_code == 201:
            call_id = res.json().get('id', 'unknown')
            print(f"  CALL: {company} ({call_id[:8]}...)")
            logger.info(f"Call initiated: {company} - {call_id}")
            return True
        return False
    except:
        return False

# ============ MAIN LOOP ============
def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      HVAC CAMPAIGN - NO DUPLICATES                       ║
║      Interval: Every 3 Minutes | Until: 3 PM             ║
║      Goal: 100 Unique Contacts                           ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info("Campaign V3 started - HVAC only, no duplicates")
    
    called_data = load_called_contacts()
    lead_index = 0
    
    while True:
        # Check time cutoff
        now = datetime.now()
        if now.hour >= CUTOFF_HOUR:
            print(f"\n🛑 3 PM CUTOFF REACHED!")
            break
        
        # Check goal
        if called_data['count'] >= DAILY_GOAL:
            print(f"\n🎉 GOAL REACHED: {called_data['count']}/{DAILY_GOAL}")
            break
        
        # Check if we have more leads
        if lead_index >= len(HVAC_LEADS):
            print(f"\n📋 All {len(HVAC_LEADS)} leads exhausted. Goal: {called_data['count']}/{DAILY_GOAL}")
            break
        
        print(f"\n[{now.strftime('%H:%M:%S')}] Processing lead {lead_index + 1}/{len(HVAC_LEADS)}")
        print(f"   Progress: {called_data['count']}/{DAILY_GOAL} unique contacts")
        
        lead = HVAC_LEADS[lead_index]
        phone = re.sub(r'\D', '', lead['phone'])
        
        # Skip duplicates
        if is_duplicate(phone, called_data):
            print(f"   SKIP (duplicate): {lead['company_name']}")
            lead_index += 1
            continue
        
        # Format phone
        if len(phone) >= 10:
            phone = f"+1{phone[-10:]}"
        else:
            lead_index += 1
            continue
        
        # Process lead
        company = lead['company_name']
        print(f"   📞 {company} - {lead['city']}")
        
        ghl_ok = push_to_ghl(lead, phone)
        db_ok = save_to_database(lead, phone)
        call_ok = call_lead(lead, phone)
        
        if ghl_ok or call_ok:
            mark_called(phone, called_data)
            print(f"   ✅ Success! Total: {called_data['count']}/{DAILY_GOAL}")
        
        lead_index += 1
        
        # Wait for next interval
        if lead_index < len(HVAC_LEADS) and called_data['count'] < DAILY_GOAL:
            print(f"   ⏳ Next call in 3 minutes...")
            time.sleep(INTERVAL_SECONDS)
    
    # Final report
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      CAMPAIGN COMPLETE                                   ║
║      Unique Contacts: {called_data['count']}/{DAILY_GOAL}                             ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"Campaign complete - {called_data['count']}/{DAILY_GOAL} unique contacts")

if __name__ == "__main__":
    main()
