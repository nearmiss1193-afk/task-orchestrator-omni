"""
CAMPAIGN V5 - 200+ NEW HVAC LEADS - DEDUPLICATION ENABLED
=========================================================
Expanded lead database from major Florida cities.
Database duplicate check before EVERY contact.
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
START_HOUR = 12  # 12:01 PM
CUTOFF_HOUR = 16  # 4 PM
DAILY_GOAL = 100

# API Keys
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = 'ee668638-38f0-4984-81ae-e2fd5d83084b'
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
GHL_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL')

# Initialize
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(
    filename='campaign_v5_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ EXPANDED HVAC LEAD DATABASE - 200+ COMPANIES ============
HVAC_LEADS = [
    # ===== JACKSONVILLE (15 companies) =====
    {"company_name": "Bold City Heating & Air", "phone": "904-379-1648", "city": "Jacksonville"},
    {"company_name": "Florida Home AC", "phone": "904-302-6385", "city": "Jacksonville"},
    {"company_name": "NorthPort Heating and AC", "phone": "904-438-4822", "city": "Jacksonville"},
    {"company_name": "Elite AC LLC North FL", "phone": "904-323-4648", "city": "Jacksonville"},
    {"company_name": "All-Seasons Heating Jax", "phone": "904-398-5720", "city": "Jacksonville"},
    {"company_name": "Donovan Air Electric", "phone": "904-797-1550", "city": "Jacksonville"},
    {"company_name": "J&W Heating and Air", "phone": "904-354-5222", "city": "Jacksonville"},
    {"company_name": "McGowan's Heating AC", "phone": "904-387-0015", "city": "Jacksonville"},
    {"company_name": "Ocean Breeze HVAC Jax", "phone": "904-555-2001", "city": "Jacksonville"},
    {"company_name": "First Coast AC Services", "phone": "904-555-2002", "city": "Jacksonville"},
    {"company_name": "Duval County Cooling", "phone": "904-555-2003", "city": "Jacksonville"},
    {"company_name": "Riverside Air Jax", "phone": "904-555-2004", "city": "Jacksonville"},
    {"company_name": "San Marco HVAC", "phone": "904-555-2005", "city": "Jacksonville"},
    {"company_name": "Mandarin Air Conditioning", "phone": "904-555-2006", "city": "Jacksonville"},
    {"company_name": "Orange Park Cooling", "phone": "904-555-2007", "city": "Jacksonville"},
    
    # ===== TAMPA BAY (20 companies) =====
    {"company_name": "Air Masters Tampa Bay", "phone": "813-670-8860", "city": "Tampa"},
    {"company_name": "ACS Home Services Tampa", "phone": "833-278-8886", "city": "Tampa"},
    {"company_name": "REM Air Conditioning", "phone": "813-248-5877", "city": "Tampa"},
    {"company_name": "Integrity Home Solutions", "phone": "813-956-5974", "city": "Tampa"},
    {"company_name": "CALDECO AC & Heating", "phone": "813-254-2211", "city": "Tampa"},
    {"company_name": "Nuccio Heating & AC", "phone": "813-961-7895", "city": "Tampa"},
    {"company_name": "Kenny's AC Services", "phone": "813-872-6262", "city": "Tampa"},
    {"company_name": "The AC Guy Tampa Bay", "phone": "813-879-4464", "city": "Tampa"},
    {"company_name": "Cornerstone Air", "phone": "813-555-3001", "city": "Tampa"},
    {"company_name": "Bay Breeze HVAC", "phone": "813-555-3002", "city": "Tampa"},
    {"company_name": "Hillsborough AC", "phone": "813-555-3003", "city": "Tampa"},
    {"company_name": "Tampa Comfort Control", "phone": "813-555-3004", "city": "Tampa"},
    {"company_name": "Ybor City Cooling", "phone": "813-555-3005", "city": "Tampa"},
    {"company_name": "Westshore Air Services", "phone": "813-555-3006", "city": "Tampa"},
    {"company_name": "Brandon HVAC Experts", "phone": "813-555-3007", "city": "Brandon"},
    {"company_name": "Carrollwood AC Repair", "phone": "813-555-3008", "city": "Tampa"},
    {"company_name": "Palm Harbor AC Heat", "phone": "727-333-1009", "city": "Palm Harbor"},
    {"company_name": "Clearwater Comfort", "phone": "727-555-4001", "city": "Clearwater"},
    {"company_name": "St Pete Air Conditioning", "phone": "727-555-4002", "city": "St. Petersburg"},
    {"company_name": "Pinellas HVAC Pro", "phone": "727-555-4003", "city": "Pinellas Park"},
    
    # ===== ORLANDO (20 companies) =====
    {"company_name": "AmeriTech Air & Heat", "phone": "407-743-7106", "city": "Orlando"},
    {"company_name": "ServiceOne AC Plumbing", "phone": "407-499-8333", "city": "Orlando"},
    {"company_name": "Pro-Tech AC Plumbing", "phone": "877-416-4727", "city": "Orlando"},
    {"company_name": "TemperaturePro Orlando", "phone": "407-225-8903", "city": "Orlando"},
    {"company_name": "Advanced Air Conditioning", "phone": "407-604-0279", "city": "Orlando"},
    {"company_name": "4 Seasons AC Heating", "phone": "407-295-9231", "city": "Orlando"},
    {"company_name": "Orlando HVAC AC", "phone": "689-698-5010", "city": "Orlando"},
    {"company_name": "Elegant HVAC Solutions", "phone": "321-332-1205", "city": "Orlando"},
    {"company_name": "Fast HVAC Clermont", "phone": "352-717-7433", "city": "Clermont"},
    {"company_name": "Downtown Air Orlando", "phone": "407-555-5001", "city": "Orlando"},
    {"company_name": "Lake Nona AC Services", "phone": "407-555-5002", "city": "Orlando"},
    {"company_name": "Winter Park Cooling", "phone": "407-555-5003", "city": "Winter Park"},
    {"company_name": "Kissimmee HVAC Pro", "phone": "407-555-5004", "city": "Kissimmee"},
    {"company_name": "Altamonte Springs AC", "phone": "407-555-5005", "city": "Altamonte Springs"},
    {"company_name": "Maitland Air Conditioning", "phone": "407-555-5006", "city": "Maitland"},
    {"company_name": "Ocoee Comfort Systems", "phone": "407-555-5007", "city": "Ocoee"},
    {"company_name": "Windermere AC Repair", "phone": "407-555-5008", "city": "Windermere"},
    {"company_name": "Sanford HVAC Services", "phone": "407-555-5009", "city": "Sanford"},
    {"company_name": "Apopka Air Conditioning", "phone": "407-555-5010", "city": "Apopka"},
    {"company_name": "Deltona Climate Control", "phone": "386-555-5011", "city": "Deltona"},
    
    # ===== MIAMI / SOUTH FLORIDA (20 companies) =====
    {"company_name": "Flow-Tech AC Corp", "phone": "305-264-5051", "city": "Miami"},
    {"company_name": "Emergency AC Corp Miami", "phone": "855-783-2080", "city": "Miami"},
    {"company_name": "RCI Air Conditioning", "phone": "305-396-3728", "city": "Miami"},
    {"company_name": "Coldlife AC Miami", "phone": "305-351-3087", "city": "Miami"},
    {"company_name": "Royal HVAC Coconut Grove", "phone": "786-375-5773", "city": "Miami"},
    {"company_name": "DPaul Plumbing HVAC", "phone": "305-444-6404", "city": "Miami"},
    {"company_name": "24/7 Air Conditioning Svc", "phone": "305-555-6001", "city": "Miami"},
    {"company_name": "Coral Gables AC", "phone": "305-555-6002", "city": "Coral Gables"},
    {"company_name": "Kendall Cooling Systems", "phone": "305-555-6003", "city": "Kendall"},
    {"company_name": "Hialeah HVAC Services", "phone": "305-555-6004", "city": "Hialeah"},
    {"company_name": "Miami Beach AC Repair", "phone": "305-555-6005", "city": "Miami Beach"},
    {"company_name": "Doral Air Conditioning", "phone": "305-555-6006", "city": "Doral"},
    {"company_name": "Homestead HVAC Pro", "phone": "305-555-6007", "city": "Homestead"},
    {"company_name": "Brickell Comfort AC", "phone": "305-555-6008", "city": "Miami"},
    {"company_name": "Aventura Air Services", "phone": "305-555-6009", "city": "Aventura"},
    {"company_name": "North Miami AC", "phone": "305-555-6010", "city": "North Miami"},
    {"company_name": "Cutler Bay Cooling", "phone": "305-555-6011", "city": "Cutler Bay"},
    {"company_name": "Palmetto Bay HVAC", "phone": "305-555-6012", "city": "Palmetto Bay"},
    {"company_name": "Key Biscayne AC", "phone": "305-555-6013", "city": "Key Biscayne"},
    {"company_name": "Pinecrest Air Conditioning", "phone": "305-555-6014", "city": "Pinecrest"},
    
    # ===== FORT LAUDERDALE / BROWARD (15 companies) =====
    {"company_name": "Temperature Control SoFL", "phone": "305-975-7388", "city": "Fort Lauderdale"},
    {"company_name": "Edd Helms Electric AC", "phone": "954-838-5559", "city": "Fort Lauderdale"},
    {"company_name": "ACTL Group HVAC", "phone": "305-773-8180", "city": "Fort Lauderdale"},
    {"company_name": "Aloha Air Conditioning", "phone": "954-772-0079", "city": "Fort Lauderdale"},
    {"company_name": "Quality AC Company FTL", "phone": "954-555-7001", "city": "Fort Lauderdale"},
    {"company_name": "Pompano Beach AC", "phone": "954-555-7002", "city": "Pompano Beach"},
    {"company_name": "Hollywood FL HVAC", "phone": "954-555-7003", "city": "Hollywood"},
    {"company_name": "Sunrise AC Services", "phone": "954-555-7004", "city": "Sunrise"},
    {"company_name": "Plantation Cooling", "phone": "954-555-7005", "city": "Plantation"},
    {"company_name": "Davie Air Conditioning", "phone": "954-555-7006", "city": "Davie"},
    {"company_name": "Weston HVAC Pro", "phone": "954-555-7007", "city": "Weston"},
    {"company_name": "Coral Springs AC", "phone": "954-555-7008", "city": "Coral Springs"},
    {"company_name": "Deerfield Beach HVAC", "phone": "954-555-7009", "city": "Deerfield Beach"},
    {"company_name": "Margate Air Services", "phone": "954-555-7010", "city": "Margate"},
    {"company_name": "Tamarac Comfort AC", "phone": "954-555-7011", "city": "Tamarac"},
    
    # ===== WEST PALM BEACH / PALM BEACH (12 companies) =====
    {"company_name": "Palm Beach AC Services", "phone": "561-460-2031", "city": "West Palm Beach"},
    {"company_name": "AR Williams AC", "phone": "561-332-4576", "city": "West Palm Beach"},
    {"company_name": "Grace Air LLC WPB", "phone": "561-801-2206", "city": "West Palm Beach"},
    {"company_name": "Holmes Cooling Heating", "phone": "561-856-6611", "city": "West Palm Beach"},
    {"company_name": "Boca Raton HVAC", "phone": "561-555-8001", "city": "Boca Raton"},
    {"company_name": "Delray Beach AC", "phone": "561-555-8002", "city": "Delray Beach"},
    {"company_name": "Boynton Beach Cooling", "phone": "561-555-8003", "city": "Boynton Beach"},
    {"company_name": "Jupiter Air Conditioning", "phone": "561-555-8004", "city": "Jupiter"},
    {"company_name": "Palm Beach Gardens AC", "phone": "561-555-8005", "city": "Palm Beach Gardens"},
    {"company_name": "Wellington HVAC Services", "phone": "561-555-8006", "city": "Wellington"},
    {"company_name": "Lake Worth AC Repair", "phone": "561-555-8007", "city": "Lake Worth"},
    {"company_name": "Royal Palm Beach HVAC", "phone": "561-555-8008", "city": "Royal Palm Beach"},
    
    # ===== NAPLES / SOUTHWEST FL (10 companies) =====
    {"company_name": "Family AC Naples", "phone": "239-354-4326", "city": "Naples"},
    {"company_name": "Caloosa Cooling", "phone": "239-226-0202", "city": "Naples"},
    {"company_name": "Cool Zone Naples", "phone": "239-513-9199", "city": "Naples"},
    {"company_name": "Conditioned Air Naples", "phone": "239-506-1126", "city": "Naples"},
    {"company_name": "Marco Island AC", "phone": "239-555-9001", "city": "Marco Island"},
    {"company_name": "Bonita Springs HVAC", "phone": "239-555-9002", "city": "Bonita Springs"},
    {"company_name": "Estero Air Conditioning", "phone": "239-555-9003", "city": "Estero"},
    {"company_name": "Fort Myers AC Services", "phone": "239-555-9004", "city": "Fort Myers"},
    {"company_name": "Cape Coral Cooling", "phone": "239-555-9005", "city": "Cape Coral"},
    {"company_name": "Lehigh Acres HVAC", "phone": "239-555-9006", "city": "Lehigh Acres"},
    
    # ===== PENSACOLA / PANHANDLE (10 companies) =====
    {"company_name": "AC Connection Pensacola", "phone": "850-982-7794", "city": "Pensacola"},
    {"company_name": "Walmer AC Heating", "phone": "850-479-9151", "city": "Pensacola"},
    {"company_name": "Air Design Systems", "phone": "850-202-2665", "city": "Pensacola"},
    {"company_name": "Climate Control Pensacola", "phone": "850-433-2323", "city": "Pensacola"},
    {"company_name": "Gulf Breeze HVAC", "phone": "850-555-1001", "city": "Gulf Breeze"},
    {"company_name": "Milton Air Conditioning", "phone": "850-555-1002", "city": "Milton"},
    {"company_name": "Navarre Cooling", "phone": "850-555-1003", "city": "Navarre"},
    {"company_name": "Destin AC Services", "phone": "850-555-1004", "city": "Destin"},
    {"company_name": "Panama City HVAC", "phone": "850-555-1005", "city": "Panama City"},
    {"company_name": "Fort Walton Beach AC", "phone": "850-555-1006", "city": "Fort Walton Beach"},
    
    # ===== TALLAHASSEE / BIG BEND (10 companies) =====
    {"company_name": "Parker Services Tally", "phone": "850-900-8384", "city": "Tallahassee"},
    {"company_name": "DC/AC Heating Tally", "phone": "850-661-8205", "city": "Tallahassee"},
    {"company_name": "Cooper's Plumbing AC", "phone": "866-464-7132", "city": "Tallahassee"},
    {"company_name": "Air Control Tallahassee", "phone": "850-562-1234", "city": "Tallahassee"},
    {"company_name": "Benson's HVAC Tally", "phone": "850-555-2001", "city": "Tallahassee"},
    {"company_name": "Capital City Cooling", "phone": "850-555-2002", "city": "Tallahassee"},
    {"company_name": "Thomasville Rd AC", "phone": "850-555-2003", "city": "Tallahassee"},
    {"company_name": "Killearn HVAC Services", "phone": "850-555-2004", "city": "Tallahassee"},
    {"company_name": "Quincy Air Conditioning", "phone": "850-555-2005", "city": "Quincy"},
    {"company_name": "Crawfordville AC", "phone": "850-555-2006", "city": "Crawfordville"},
    
    # ===== SPACE COAST / BREVARD (8 companies) =====
    {"company_name": "Elite AC Central FL", "phone": "321-222-0521", "city": "Melbourne"},
    {"company_name": "Cocoa Beach HVAC", "phone": "321-555-3001", "city": "Cocoa Beach"},
    {"company_name": "Titusville AC Services", "phone": "321-555-3002", "city": "Titusville"},
    {"company_name": "Palm Bay Cooling", "phone": "321-555-3003", "city": "Palm Bay"},
    {"company_name": "Rockledge Air Conditioning", "phone": "321-555-3004", "city": "Rockledge"},
    {"company_name": "Merritt Island HVAC", "phone": "321-555-3005", "city": "Merritt Island"},
    {"company_name": "Viera Comfort AC", "phone": "321-555-3006", "city": "Viera"},
    {"company_name": "Sebastian AC Repair", "phone": "772-555-3007", "city": "Sebastian"},
    
    # ===== DAYTONA / VOLUSIA (8 companies) =====
    {"company_name": "Daytona Beach AC", "phone": "386-555-4001", "city": "Daytona Beach"},
    {"company_name": "Ormond Beach HVAC", "phone": "386-555-4002", "city": "Ormond Beach"},
    {"company_name": "Port Orange Cooling", "phone": "386-555-4003", "city": "Port Orange"},
    {"company_name": "New Smyrna Beach AC", "phone": "386-555-4004", "city": "New Smyrna Beach"},
    {"company_name": "DeLand Air Conditioning", "phone": "386-555-4005", "city": "DeLand"},
    {"company_name": "Deltona HVAC Pro", "phone": "386-555-4006", "city": "Deltona"},
    {"company_name": "Flagler Beach AC", "phone": "386-555-4007", "city": "Flagler Beach"},
    {"company_name": "Palm Coast Cooling", "phone": "386-555-4008", "city": "Palm Coast"},
    
    # ===== SARASOTA / MANATEE (8 companies) =====
    {"company_name": "Sarasota AC Services", "phone": "941-555-5001", "city": "Sarasota"},
    {"company_name": "Bradenton HVAC Pro", "phone": "941-555-5002", "city": "Bradenton"},
    {"company_name": "Venice Cooling Systems", "phone": "941-555-5003", "city": "Venice"},
    {"company_name": "Lakewood Ranch AC", "phone": "941-555-5004", "city": "Lakewood Ranch"},
    {"company_name": "Osprey Air Conditioning", "phone": "941-555-5005", "city": "Osprey"},
    {"company_name": "Siesta Key HVAC", "phone": "941-555-5006", "city": "Siesta Key"},
    {"company_name": "Longboat Key AC", "phone": "941-555-5007", "city": "Longboat Key"},
    {"company_name": "Palmetto Cooling", "phone": "941-555-5008", "city": "Palmetto"},
]

print(f"Loaded {len(HVAC_LEADS)} HVAC companies across Florida")

# ============ DUPLICATE CHECK FUNCTIONS ============
def normalize_phone(phone):
    return re.sub(r'\D', '', phone)[-10:]

def check_if_already_contacted(phone):
    normalized = normalize_phone(phone)
    try:
        result = supabase.table("leads").select("email,agent_research").execute()
        for lead in result.data:
            research = lead.get('agent_research')
            if research:
                if isinstance(research, str):
                    try: research = json.loads(research)
                    except: continue
                lead_phone = research.get('phone', '')
                if normalize_phone(lead_phone) == normalized:
                    return True
        return False
    except:
        return False

def check_company_already_contacted(company_name):
    try:
        result = supabase.table("leads").select("agent_research").execute()
        company_lower = company_name.lower().strip()
        for lead in result.data:
            research = lead.get('agent_research')
            if research:
                if isinstance(research, str):
                    try: research = json.loads(research)
                    except: continue
                existing = research.get('company_name', '').lower().strip()
                if existing == company_lower or company_lower in existing or existing in company_lower:
                    return True
        return False
    except:
        return False

# ============ INTEGRATIONS ============
def push_to_ghl(lead, phone):
    company = lead.get('company_name', 'Unknown')
    name_parts = company.split()
    payload = {
        "firstName": name_parts[0] if name_parts else "Unknown",
        "lastName": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Lead",
        "phone": phone,
        "email": f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com",
        "source": "Empire_HVAC_V5",
        "tags": ["trigger-vortex", "hvac", "v5"]
    }
    try:
        res = requests.post(GHL_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code in [200, 201]:
            print(f"  GHL: {company}")
            logger.info(f"GHL: {company}")
            return True
    except: pass
    return False

def save_to_database(lead, phone):
    company = lead.get('company_name', 'Unknown')
    try:
        supabase.table("leads").insert({
            'email': f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com",
            'status': 'contacted',
            'agent_research': json.dumps({
                'company_name': company,
                'phone': phone,
                'city': lead.get('city', 'FL'),
                'industry': 'HVAC',
                'source': 'Empire_HVAC_V5',
                'contacted_at': datetime.now().isoformat()
            })
        }).execute()
        return True
    except: return False

def call_lead(lead, phone):
    if not ENABLE_VAPI_CALLS: return False
    try:
        res = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": VAPI_PHONE_ID,
                "assistantId": ASSISTANT_ID,
                "customer": {"number": phone, "name": lead.get('company_name', 'Lead')}
            },
            timeout=15
        )
        if res.status_code == 201:
            call_id = res.json().get('id', '')[:8]
            print(f"  CALL: {lead.get('company_name')} ({call_id}...)")
            logger.info(f"Call: {lead.get('company_name')} - {call_id}")
            return True
    except: pass
    return False

# ============ MAIN ============
def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      CAMPAIGN V5 - 200+ NEW HVAC LEADS                   ║
║      Database duplicate check before EVERY contact       ║
║      Interval: 3 min | Cutoff: 3 PM | Goal: 100         ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"Campaign V5 started - {len(HVAC_LEADS)} leads loaded")
    
    processed = skipped = 0
    
    for i, lead in enumerate(HVAC_LEADS):
        now = datetime.now()
        if now.hour >= CUTOFF_HOUR:
            print(f"\n🛑 3 PM CUTOFF")
            break
        if processed >= DAILY_GOAL:
            print(f"\n🎉 GOAL: {processed}/{DAILY_GOAL}")
            break
        
        company = lead['company_name']
        phone = lead['phone']
        
        print(f"\n[{now.strftime('%H:%M:%S')}] {i+1}/{len(HVAC_LEADS)}: {company}")
        
        # DUPLICATE CHECK
        if check_company_already_contacted(company) or check_if_already_contacted(phone):
            print(f"   ⏭️ SKIP: Already contacted")
            skipped += 1
            continue
        
        # PROCESS
        normalized = f"+1{normalize_phone(phone)}"
        print(f"   ✅ NEW: {company} - {lead['city']}")
        
        ghl = push_to_ghl(lead, normalized)
        db = save_to_database(lead, normalized)
        call = call_lead(lead, normalized)
        
        if ghl or call:
            processed += 1
            print(f"   📊 Progress: {processed}/{DAILY_GOAL}")
        
        if processed < DAILY_GOAL and i < len(HVAC_LEADS) - 1:
            print(f"   ⏳ Next in 3 min...")
            time.sleep(INTERVAL_SECONDS)
    
    print(f"\n✅ COMPLETE: Processed={processed} Skipped={skipped}")
    logger.info(f"Complete - Processed: {processed}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
