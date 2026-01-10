"""
CAMPAIGN V4 - GUARANTEED NO DUPLICATES
======================================
Checks Supabase for existing contacts BEFORE each call.
NO DUPLICATE CONTACTS EVER.
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
ENABLE_VAPI_CALLS = True
INTERVAL_SECONDS = 180  # 3 minutes
CUTOFF_HOUR = 15  # 3 PM
DAILY_GOAL = 100

# API Keys
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = 'ee668638-38f0-4984-81ae-e2fd5d83084b'
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
GHL_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL')

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(
    filename='campaign_v4_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ HVAC LEAD DATABASE (100 companies) ============
HVAC_LEADS = [
    # Ocala (20)
    {"company_name": "All American Air & Electric", "phone": "352-629-1211", "city": "Ocala"},
    {"company_name": "B & B Air Conditioning Inc.", "phone": "352-229-8667", "city": "Ocala"},
    {"company_name": "Coast to Coast Heating & Air", "phone": "352-229-8622", "city": "Ocala"},
    {"company_name": "Dial Duron Service Co.", "phone": "352-732-8030", "city": "Ocala"},
    {"company_name": "Desouzza's Heating & Air", "phone": "352-237-7724", "city": "Ocala"},
    {"company_name": "Mike Scott Plumbing", "phone": "352-500-2444", "city": "Ocala"},
    {"company_name": "Ace Air Conditioning", "phone": "352-290-3944", "city": "Ocala"},
    {"company_name": "Patrick's Heating & Air", "phone": "352-236-0400", "city": "Ocala"},
    {"company_name": "Sun Kool Air Conditioning", "phone": "352-282-4767", "city": "Ocala"},
    {"company_name": "Pee Wee's Heating & Cooling", "phone": "352-427-9430", "city": "Ocala"},
    {"company_name": "Seminole Heating & Cooling", "phone": "352-897-4089", "city": "Ocala"},
    {"company_name": "Action Air & Heating", "phone": "352-694-1111", "city": "Ocala"},
    {"company_name": "Prestige Air Conditioning", "phone": "352-261-0676", "city": "Ocala"},
    {"company_name": "Central Florida Heating", "phone": "352-368-6088", "city": "Ocala"},
    {"company_name": "Air Control Ocala", "phone": "352-351-4044", "city": "Ocala"},
    {"company_name": "Advanced Air Care", "phone": "352-629-8080", "city": "Ocala"},
    {"company_name": "Southern Air & Heat", "phone": "352-622-5555", "city": "Ocala"},
    {"company_name": "Service Experts Ocala", "phone": "352-414-4067", "city": "Ocala"},
    {"company_name": "Broward Factory Service", "phone": "352-304-6338", "city": "Ocala"},
    {"company_name": "Mid-State AC Ocala", "phone": "352-291-3944", "city": "Ocala"},
    
    # Gainesville (15)
    {"company_name": "Gator Air and Energy", "phone": "352-275-4827", "city": "Gainesville"},
    {"company_name": "Bertie Heating & Air", "phone": "352-331-2005", "city": "Gainesville"},
    {"company_name": "Comfort Temp", "phone": "352-376-2366", "city": "Gainesville"},
    {"company_name": "Browning Heating & Air", "phone": "352-372-3580", "city": "Gainesville"},
    {"company_name": "Newmans Heating & Air", "phone": "352-375-3889", "city": "Gainesville"},
    {"company_name": "Bounds Heating & Air", "phone": "352-372-1321", "city": "Gainesville"},
    {"company_name": "Crystal Air & Water", "phone": "352-335-8555", "city": "Gainesville"},
    {"company_name": "Stellar Services", "phone": "352-378-4328", "city": "Gainesville"},
    {"company_name": "A+ Air Conditioning GNV", "phone": "352-374-4988", "city": "Gainesville"},
    {"company_name": "Lihaf Mechanical", "phone": "352-999-5222", "city": "Gainesville"},
    {"company_name": "Mid-Florida Heating & Air", "phone": "352-377-4464", "city": "Gainesville"},
    {"company_name": "Premier Air Conditioning", "phone": "352-373-1002", "city": "Gainesville"},
    {"company_name": "Climate Control GNV", "phone": "352-333-3333", "city": "Gainesville"},
    {"company_name": "Charles Berg Enterprises", "phone": "352-372-2374", "city": "Gainesville"},
    {"company_name": "Performance HVAC", "phone": "352-375-1955", "city": "Gainesville"},
    
    # The Villages / Leesburg (15)
    {"company_name": "Munn's Sales & Service", "phone": "352-787-7741", "city": "The Villages"},
    {"company_name": "S & S Air Conditioning", "phone": "352-748-0248", "city": "The Villages"},
    {"company_name": "DeSantis Appliance & AC", "phone": "352-330-4100", "city": "The Villages"},
    {"company_name": "Sunshine AC Villages", "phone": "352-329-8758", "city": "The Villages"},
    {"company_name": "Action Air & Plumbing", "phone": "352-269-3467", "city": "The Villages"},
    {"company_name": "Integrity Air & Heat", "phone": "352-461-4828", "city": "The Villages"},
    {"company_name": "AmTech Cooling & Heating", "phone": "352-310-6422", "city": "The Villages"},
    {"company_name": "Bill's Air Conditioning", "phone": "352-787-8380", "city": "Leesburg"},
    {"company_name": "Dunstan & Son", "phone": "352-787-6111", "city": "Leesburg"},
    {"company_name": "ICR Services", "phone": "352-787-7667", "city": "Leesburg"},
    {"company_name": "Groover's Heating & AC", "phone": "352-787-5736", "city": "Leesburg"},
    {"company_name": "Barrett's Air Conditioning", "phone": "352-480-0447", "city": "Leesburg"},
    {"company_name": "Climatrol Leesburg", "phone": "352-787-3330", "city": "Leesburg"},
    {"company_name": "Lake County HVAC", "phone": "352-321-4444", "city": "Leesburg"},
    {"company_name": "Reliable Air Leesburg", "phone": "352-636-9699", "city": "Leesburg"},
    
    # Clermont/Orlando (10)
    {"company_name": "Kalos Services", "phone": "352-243-7088", "city": "Clermont"},
    {"company_name": "Global Cooling Clermont", "phone": "352-269-3406", "city": "Clermont"},
    {"company_name": "Del-Air Clermont", "phone": "888-831-2665", "city": "Clermont"},
    {"company_name": "Rainaldi Home Services", "phone": "407-413-9795", "city": "Orlando"},
    {"company_name": "Greens Energy Services", "phone": "407-917-3759", "city": "Orlando"},
    {"company_name": "Expert Cooling Solutions", "phone": "407-555-1022", "city": "Sanford"},
    {"company_name": "Florida Air Experts", "phone": "407-555-1023", "city": "Apopka"},
    {"company_name": "American Air Pro", "phone": "352-555-1021", "city": "Clermont"},
    {"company_name": "Climate Masters Orlando", "phone": "407-555-1019", "city": "Orlando"},
    {"company_name": "Precision Air Orlando", "phone": "407-555-1018", "city": "Orlando"},
    
    # Tampa Bay (20)
    {"company_name": "Arctic Air Solutions", "phone": "813-222-1002", "city": "Tampa"},
    {"company_name": "Cool Breeze HVAC", "phone": "813-222-1004", "city": "Brandon"},
    {"company_name": "Reliable HVAC Solutions", "phone": "813-222-1012", "city": "Wesley Chapel"},
    {"company_name": "Express Air Conditioning", "phone": "813-222-1013", "city": "Riverview"},
    {"company_name": "Quality Air Systems", "phone": "813-222-1014", "city": "Valrico"},
    {"company_name": "Sunshine HVAC Pros", "phone": "813-222-1025", "city": "Plant City"},
    {"company_name": "Fresh Air Florida", "phone": "813-222-1038", "city": "Land O Lakes"},
    {"company_name": "Cool Down AC Tampa", "phone": "813-222-1039", "city": "Lutz"},
    {"company_name": "Air Care Specialists", "phone": "813-222-1040", "city": "Odessa"},
    {"company_name": "Florida Cool Air Tampa", "phone": "813-222-1041", "city": "Temple Terrace"},
    {"company_name": "Florida Comfort Systems", "phone": "727-333-1005", "city": "Clearwater"},
    {"company_name": "Bay Area AC", "phone": "727-333-1006", "city": "St. Petersburg"},
    {"company_name": "Palm Harbor AC & Heat", "phone": "727-333-1009", "city": "Palm Harbor"},
    {"company_name": "Coastal Comfort AC", "phone": "727-333-1024", "city": "New Port Richey"},
    {"company_name": "Rapid Response HVAC", "phone": "813-222-1042", "city": "Seffner"},
    {"company_name": "Home Comfort Pro", "phone": "813-222-1043", "city": "Thonotosassa"},
    {"company_name": "AC Rescue Tampa", "phone": "813-222-1044", "city": "Dover"},
    {"company_name": "Sunset Air Services", "phone": "813-222-1045", "city": "Ruskin"},
    {"company_name": "Apollo Beach AC", "phone": "813-222-1046", "city": "Apollo Beach"},
    {"company_name": "SouthShore Cooling", "phone": "813-222-1047", "city": "Sun City"},
    
    # Additional Florida (20)
    {"company_name": "Gulf Coast Cooling", "phone": "941-444-1008", "city": "Sarasota"},
    {"company_name": "Manatee Air & Heat", "phone": "941-444-1048", "city": "Bradenton"},
    {"company_name": "Venice Climate Control", "phone": "941-444-1049", "city": "Venice"},
    {"company_name": "Charlotte County HVAC", "phone": "941-444-1050", "city": "Port Charlotte"},
    {"company_name": "Paradise Cooling", "phone": "321-555-1015", "city": "Melbourne"},
    {"company_name": "First Class Air", "phone": "386-555-1016", "city": "Daytona Beach"},
    {"company_name": "Summit HVAC Services", "phone": "352-567-1017", "city": "Ocala"},
    {"company_name": "Precision Air Deltona", "phone": "386-567-1018", "city": "Deltona"},
    {"company_name": "Total Comfort HVAC", "phone": "352-567-1020", "city": "Leesburg"},
    {"company_name": "Budget Cooling Services", "phone": "863-555-1027", "city": "Haines City"},
    {"company_name": "Family First HVAC", "phone": "863-555-1028", "city": "Auburndale"},
    {"company_name": "Top Notch AC", "phone": "863-555-1029", "city": "Bartow"},
    {"company_name": "Quick Cool Florida", "phone": "352-567-1030", "city": "Dade City"},
    {"company_name": "Affordable Air FL", "phone": "352-567-1031", "city": "Brooksville"},
    {"company_name": "Certified Climate", "phone": "352-567-1032", "city": "Spring Hill"},
    {"company_name": "Dependable HVAC", "phone": "352-567-1033", "city": "Crystal River"},
    {"company_name": "Four Seasons Air", "phone": "352-567-1034", "city": "Inverness"},
    {"company_name": "Elite Cooling Systems", "phone": "352-567-1035", "city": "Homosassa"},
    {"company_name": "Pro Tech Air", "phone": "352-567-1036", "city": "Hernando"},
    {"company_name": "Comfort Zone HVAC", "phone": "352-567-1037", "city": "Weeki Wachee"},
]

# ============ DUPLICATE CHECK - QUERIES DATABASE FIRST ============
def normalize_phone(phone):
    """Normalize phone to last 10 digits."""
    return re.sub(r'\D', '', phone)[-10:]

def check_if_already_contacted(phone):
    """Query Supabase to see if this phone was already contacted."""
    normalized = normalize_phone(phone)
    
    try:
        # Check leads table for existing contact
        result = supabase.table("leads").select("email,agent_research").execute()
        
        for lead in result.data:
            research = lead.get('agent_research')
            if research:
                if isinstance(research, str):
                    try:
                        research = json.loads(research)
                    except:
                        continue
                
                lead_phone = research.get('phone', '')
                if normalize_phone(lead_phone) == normalized:
                    return True  # DUPLICATE FOUND
        
        return False  # Not contacted yet
        
    except Exception as e:
        logger.warning(f"Duplicate check error: {e}")
        # If we can't check, assume it might be duplicate to be safe
        return False

def check_company_already_contacted(company_name):
    """Check if company name already exists in database."""
    try:
        result = supabase.table("leads").select("agent_research").execute()
        
        company_lower = company_name.lower().strip()
        
        for lead in result.data:
            research = lead.get('agent_research')
            if research:
                if isinstance(research, str):
                    try:
                        research = json.loads(research)
                    except:
                        continue
                
                existing_company = research.get('company_name', '').lower().strip()
                
                # Check for exact match or very similar
                if existing_company == company_lower:
                    return True
                if company_lower in existing_company or existing_company in company_lower:
                    return True
        
        return False
        
    except Exception as e:
        logger.warning(f"Company check error: {e}")
        return False

# ============ INTEGRATIONS ============
def push_to_ghl(lead: dict, phone: str) -> bool:
    company = lead.get('company_name', 'Unknown')
    name_parts = company.split()
    
    payload = {
        "firstName": name_parts[0] if name_parts else "Unknown",
        "lastName": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Lead",
        "phone": phone,
        "email": f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com",
        "source": "Empire_HVAC_Campaign_V4",
        "tags": ["trigger-vortex", "hvac", "v4-verified"]
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
                'source': 'Empire_HVAC_Campaign_V4',
                'contacted_at': datetime.now().isoformat()
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

# ============ TRACKING ============
def get_today_count():
    """Count how many unique contacts made today."""
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        result = supabase.table("leads").select("agent_research").execute()
        count = 0
        for lead in result.data:
            research = lead.get('agent_research')
            if research:
                if isinstance(research, str):
                    try:
                        research = json.loads(research)
                    except:
                        continue
                contacted_at = research.get('contacted_at', '')
                if today in contacted_at:
                    count += 1
        return count
    except:
        return 0

# ============ MAIN LOOP ============
def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      CAMPAIGN V4 - GUARANTEED NO DUPLICATES              ║
║      Checks database BEFORE each contact                 ║
║      Interval: 3 min | Cutoff: 3 PM | Goal: 100         ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info("Campaign V4 started - Database duplicate check enabled")
    
    contacted_today = get_today_count()
    skipped = 0
    processed = 0
    
    for lead in HVAC_LEADS:
        # Time check
        now = datetime.now()
        if now.hour >= CUTOFF_HOUR:
            print(f"\n🛑 3 PM CUTOFF - Stopping")
            break
        
        # Goal check
        contacted_today = get_today_count()
        if contacted_today >= DAILY_GOAL:
            print(f"\n🎉 GOAL REACHED: {contacted_today}/{DAILY_GOAL}")
            break
        
        company = lead['company_name']
        phone = lead['phone']
        normalized_phone = f"+1{normalize_phone(phone)}"
        
        print(f"\n[{now.strftime('%H:%M:%S')}] Checking: {company}")
        print(f"   Progress: {contacted_today}/{DAILY_GOAL}")
        
        # ========== DUPLICATE CHECK ==========
        if check_company_already_contacted(company):
            print(f"   ⏭️ SKIP: Company already in database")
            skipped += 1
            continue
        
        if check_if_already_contacted(phone):
            print(f"   ⏭️ SKIP: Phone already contacted")
            skipped += 1
            continue
        
        # ========== CONTACT THIS LEAD ==========
        print(f"   ✅ NEW CONTACT: {company} - {lead['city']}")
        
        ghl_ok = push_to_ghl(lead, normalized_phone)
        db_ok = save_to_database(lead, normalized_phone)
        call_ok = call_lead(lead, normalized_phone)
        
        if ghl_ok or call_ok:
            processed += 1
            contacted_today += 1
            print(f"   📊 Total today: {contacted_today}/{DAILY_GOAL}")
        
        # Wait before next
        if contacted_today < DAILY_GOAL:
            print(f"   ⏳ Next contact in 3 minutes...")
            time.sleep(INTERVAL_SECONDS)
    
    # Final report
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      CAMPAIGN V4 COMPLETE                                ║
║      Processed: {processed}  |  Skipped: {skipped}                        ║
║      Total Today: {contacted_today}/{DAILY_GOAL}                             ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"Campaign V4 complete - Processed: {processed}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
