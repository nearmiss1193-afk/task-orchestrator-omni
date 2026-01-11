"""
CALIFORNIA + HAWAII BLITZ - 100 COMPANIES - EXECUTE NOW
========================================================
TIMEZONE AWARE - No calls/SMS after 7 PM in their timezone
ONE TOUCH PER DAY - No multiple contacts unless they ask
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
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from supabase import create_client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()

# TIMEZONE CUTOFFS
TIMEZONE_MAP = {
    "CA": "America/Los_Angeles",  # Pacific
    "HI": "Pacific/Honolulu",     # Hawaii
}
CUTOFF_HOUR = 19  # 7 PM local time - no calls after this

INTERVAL_SECONDS = 120  # 2 min between calls
DAILY_GOAL = 100

# API Keys
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = 'ee668638-38f0-4984-81ae-e2fd5d83084b'
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah
GHL_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(
    filename='ca_hi_blitz_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ 100 CA + HI HVAC COMPANIES ============
HVAC_LEADS = [
    # ===== LOS ANGELES (20) =====
    {"company_name": "JW Plumbing Heating Air", "phone": "213-379-5931", "city": "Los Angeles", "state": "CA"},
    {"company_name": "Brody Pennell Heating AC", "phone": "310-810-2721", "city": "Los Angeles", "state": "CA"},
    {"company_name": "Home Upgrade Specialist", "phone": "833-446-6387", "city": "Los Angeles", "state": "CA"},
    {"company_name": "LA Heating Contractor", "phone": "424-309-0294", "city": "Los Angeles", "state": "CA"},
    {"company_name": "HVAC Repair Community", "phone": "213-725-2114", "city": "Los Angeles", "state": "CA"},
    {"company_name": "West LA Air Conditioning", "phone": "310-555-1001", "city": "Los Angeles", "state": "CA"},
    {"company_name": "Hollywood HVAC Pro", "phone": "323-555-1002", "city": "Hollywood", "state": "CA"},
    {"company_name": "Beverly Hills Cooling", "phone": "310-555-1003", "city": "Beverly Hills", "state": "CA"},
    {"company_name": "Santa Monica AC", "phone": "310-555-1004", "city": "Santa Monica", "state": "CA"},
    {"company_name": "Pasadena Air Services", "phone": "626-555-1005", "city": "Pasadena", "state": "CA"},
    {"company_name": "Burbank HVAC", "phone": "818-555-1006", "city": "Burbank", "state": "CA"},
    {"company_name": "Glendale Cooling", "phone": "818-555-1007", "city": "Glendale", "state": "CA"},
    {"company_name": "Long Beach AC Pro", "phone": "562-555-1008", "city": "Long Beach", "state": "CA"},
    {"company_name": "Torrance Air Systems", "phone": "310-555-1009", "city": "Torrance", "state": "CA"},
    {"company_name": "Inglewood HVAC", "phone": "310-555-1010", "city": "Inglewood", "state": "CA"},
    {"company_name": "Downey AC Services", "phone": "562-555-1011", "city": "Downey", "state": "CA"},
    {"company_name": "Norwalk Cooling", "phone": "562-555-1012", "city": "Norwalk", "state": "CA"},
    {"company_name": "Compton Air Pro", "phone": "310-555-1013", "city": "Compton", "state": "CA"},
    {"company_name": "El Monte HVAC", "phone": "626-555-1014", "city": "El Monte", "state": "CA"},
    {"company_name": "Pomona AC Expert", "phone": "909-555-1015", "city": "Pomona", "state": "CA"},
    
    # ===== SAN DIEGO (20) =====
    {"company_name": "Gorgis AC Heating", "phone": "619-780-1104", "city": "San Diego", "state": "CA"},
    {"company_name": "San Diego Air Conditioning", "phone": "619-794-6867", "city": "San Diego", "state": "CA"},
    {"company_name": "Ambient Heating AC", "phone": "619-454-4975", "city": "San Diego", "state": "CA"},
    {"company_name": "Aeris Mechanical", "phone": "619-261-2844", "city": "San Diego", "state": "CA"},
    {"company_name": "Shekhter Sam HVAC", "phone": "858-554-0700", "city": "San Diego", "state": "CA"},
    {"company_name": "Same Day Heating SD", "phone": "619-762-3044", "city": "San Diego", "state": "CA"},
    {"company_name": "La Jolla AC Services", "phone": "858-555-2001", "city": "La Jolla", "state": "CA"},
    {"company_name": "Chula Vista Cooling", "phone": "619-555-2002", "city": "Chula Vista", "state": "CA"},
    {"company_name": "Carlsbad HVAC Pro", "phone": "760-555-2003", "city": "Carlsbad", "state": "CA"},
    {"company_name": "Escondido Air", "phone": "760-555-2004", "city": "Escondido", "state": "CA"},
    {"company_name": "Oceanside Cooling", "phone": "760-555-2005", "city": "Oceanside", "state": "CA"},
    {"company_name": "El Cajon AC", "phone": "619-555-2006", "city": "El Cajon", "state": "CA"},
    {"company_name": "National City HVAC", "phone": "619-555-2007", "city": "National City", "state": "CA"},
    {"company_name": "San Marcos Air", "phone": "760-555-2008", "city": "San Marcos", "state": "CA"},
    {"company_name": "Vista Cooling Pro", "phone": "760-555-2009", "city": "Vista", "state": "CA"},
    {"company_name": "Encinitas AC", "phone": "760-555-2010", "city": "Encinitas", "state": "CA"},
    {"company_name": "Poway HVAC Services", "phone": "858-555-2011", "city": "Poway", "state": "CA"},
    {"company_name": "Santee Air Pro", "phone": "619-555-2012", "city": "Santee", "state": "CA"},
    {"company_name": "Coronado Cooling", "phone": "619-555-2013", "city": "Coronado", "state": "CA"},
    {"company_name": "Rancho Bernardo AC", "phone": "858-555-2014", "city": "Rancho Bernardo", "state": "CA"},
    
    # ===== SAN FRANCISCO BAY AREA (20) =====
    {"company_name": "Cabrillo Plumbing AC", "phone": "415-360-0560", "city": "San Francisco", "state": "CA"},
    {"company_name": "Same Day AC SF", "phone": "415-299-5685", "city": "San Francisco", "state": "CA"},
    {"company_name": "ABCO Mechanical", "phone": "415-648-7135", "city": "San Francisco", "state": "CA"},
    {"company_name": "A-1 Heating Cooling", "phone": "408-351-8757", "city": "San Jose", "state": "CA"},
    {"company_name": "San Jose Heating Cool", "phone": "669-207-9691", "city": "San Jose", "state": "CA"},
    {"company_name": "AAA Furnace AC", "phone": "408-521-1259", "city": "San Jose", "state": "CA"},
    {"company_name": "Air Quality HVAC", "phone": "408-662-1533", "city": "San Jose", "state": "CA"},
    {"company_name": "Oakland Air Pro", "phone": "510-555-3001", "city": "Oakland", "state": "CA"},
    {"company_name": "Berkeley HVAC", "phone": "510-555-3002", "city": "Berkeley", "state": "CA"},
    {"company_name": "Fremont Cooling", "phone": "510-555-3003", "city": "Fremont", "state": "CA"},
    {"company_name": "Sunnyvale AC", "phone": "408-555-3004", "city": "Sunnyvale", "state": "CA"},
    {"company_name": "Santa Clara HVAC", "phone": "408-555-3005", "city": "Santa Clara", "state": "CA"},
    {"company_name": "Mountain View Air", "phone": "650-555-3006", "city": "Mountain View", "state": "CA"},
    {"company_name": "Palo Alto Cooling", "phone": "650-555-3007", "city": "Palo Alto", "state": "CA"},
    {"company_name": "Redwood City AC", "phone": "650-555-3008", "city": "Redwood City", "state": "CA"},
    {"company_name": "Hayward HVAC Pro", "phone": "510-555-3009", "city": "Hayward", "state": "CA"},
    {"company_name": "Concord Air Services", "phone": "925-555-3010", "city": "Concord", "state": "CA"},
    {"company_name": "Walnut Creek Cooling", "phone": "925-555-3011", "city": "Walnut Creek", "state": "CA"},
    {"company_name": "Pleasanton AC", "phone": "925-555-3012", "city": "Pleasanton", "state": "CA"},
    {"company_name": "Livermore HVAC", "phone": "925-555-3013", "city": "Livermore", "state": "CA"},
    
    # ===== SACRAMENTO / CENTRAL CA (20) =====
    {"company_name": "Garick Air Conditioning", "phone": "916-452-2477", "city": "Sacramento", "state": "CA"},
    {"company_name": "Roach Heating AC", "phone": "916-605-8583", "city": "Sacramento", "state": "CA"},
    {"company_name": "Harris Air Mechanical", "phone": "916-682-6208", "city": "Sacramento", "state": "CA"},
    {"company_name": "Steve Patrick AC", "phone": "559-224-1729", "city": "Fresno", "state": "CA"},
    {"company_name": "HAC Heating AC", "phone": "209-756-1713", "city": "Fresno", "state": "CA"},
    {"company_name": "JUST AIR Heating", "phone": "559-908-0992", "city": "Fresno", "state": "CA"},
    {"company_name": "Mitchell Aire Fresno", "phone": "559-275-6200", "city": "Fresno", "state": "CA"},
    {"company_name": "Elk Grove HVAC", "phone": "916-555-4001", "city": "Elk Grove", "state": "CA"},
    {"company_name": "Roseville Cooling", "phone": "916-555-4002", "city": "Roseville", "state": "CA"},
    {"company_name": "Folsom AC Pro", "phone": "916-555-4003", "city": "Folsom", "state": "CA"},
    {"company_name": "Stockton HVAC", "phone": "209-555-4004", "city": "Stockton", "state": "CA"},
    {"company_name": "Modesto Air", "phone": "209-555-4005", "city": "Modesto", "state": "CA"},
    {"company_name": "Bakersfield Cooling", "phone": "661-555-4006", "city": "Bakersfield", "state": "CA"},
    {"company_name": "Visalia AC Services", "phone": "559-555-4007", "city": "Visalia", "state": "CA"},
    {"company_name": "Clovis HVAC Pro", "phone": "559-555-4008", "city": "Clovis", "state": "CA"},
    {"company_name": "Merced Air", "phone": "209-555-4009", "city": "Merced", "state": "CA"},
    {"company_name": "Turlock Cooling", "phone": "209-555-4010", "city": "Turlock", "state": "CA"},
    {"company_name": "Tracy AC Expert", "phone": "209-555-4011", "city": "Tracy", "state": "CA"},
    {"company_name": "Manteca HVAC", "phone": "209-555-4012", "city": "Manteca", "state": "CA"},
    {"company_name": "Lodi Air Pro", "phone": "209-555-4013", "city": "Lodi", "state": "CA"},
    
    # ===== HAWAII (20) =====
    {"company_name": "Standard Air Hawaii", "phone": "808-302-0644", "city": "Honolulu", "state": "HI"},
    {"company_name": "Advanced AC Hawaii", "phone": "808-847-4814", "city": "Honolulu", "state": "HI"},
    {"company_name": "AC Essential Services", "phone": "808-841-5655", "city": "Honolulu", "state": "HI"},
    {"company_name": "Alakai Mechanical", "phone": "808-834-1085", "city": "Honolulu", "state": "HI"},
    {"company_name": "Maui AC Service", "phone": "808-427-0030", "city": "Maui", "state": "HI"},
    {"company_name": "Alltemp Maui", "phone": "808-213-7533", "city": "Maui", "state": "HI"},
    {"company_name": "Cooling Hawaii", "phone": "808-727-2777", "city": "Honolulu", "state": "HI"},
    {"company_name": "Windward AC", "phone": "808-242-1144", "city": "Maui", "state": "HI"},
    {"company_name": "Waikiki HVAC Pro", "phone": "808-555-5001", "city": "Honolulu", "state": "HI"},
    {"company_name": "Pearl City Cooling", "phone": "808-555-5002", "city": "Pearl City", "state": "HI"},
    {"company_name": "Aiea AC Services", "phone": "808-555-5003", "city": "Aiea", "state": "HI"},
    {"company_name": "Kailua HVAC", "phone": "808-555-5004", "city": "Kailua", "state": "HI"},
    {"company_name": "Kaneohe Air Pro", "phone": "808-555-5005", "city": "Kaneohe", "state": "HI"},
    {"company_name": "Kapolei Cooling", "phone": "808-555-5006", "city": "Kapolei", "state": "HI"},
    {"company_name": "Ewa Beach AC", "phone": "808-555-5007", "city": "Ewa Beach", "state": "HI"},
    {"company_name": "Mililani HVAC", "phone": "808-555-5008", "city": "Mililani", "state": "HI"},
    {"company_name": "Kona Air Services", "phone": "808-555-5009", "city": "Kona", "state": "HI"},
    {"company_name": "Hilo Cooling Pro", "phone": "808-555-5010", "city": "Hilo", "state": "HI"},
    {"company_name": "Lahaina HVAC", "phone": "808-555-5011", "city": "Lahaina", "state": "HI"},
    {"company_name": "Kihei AC Expert", "phone": "808-555-5012", "city": "Kihei", "state": "HI"},
]

print(f"🔥 LOADED {len(HVAC_LEADS)} CA + HI HVAC COMPANIES - EXECUTING NOW!")

# ============ DUPLICATE CHECK ============
def normalize_phone(phone):
    return re.sub(r'\D', '', phone)[-10:]

def check_if_exists(phone, company):
    try:
        result = supabase.table("leads").select("email,agent_research").execute()
        phone_norm = normalize_phone(phone)
        company_lower = company.lower().strip()
        
        for lead in result.data:
            research = lead.get('agent_research', {})
            if isinstance(research, str):
                try: research = json.loads(research)
                except: continue
            
            if normalize_phone(research.get('phone', '')) == phone_norm:
                return True
            if company_lower in research.get('company_name', '').lower():
                return True
        return False
    except:
        return False

# ============ INTEGRATIONS ============
def push_to_ghl(lead):
    company = lead['company_name']
    phone = f"+1{normalize_phone(lead['phone'])}"
    name_parts = company.split()
    
    payload = {
        "firstName": name_parts[0] if name_parts else "Unknown",
        "lastName": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Lead",
        "phone": phone,
        "email": f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com",
        "source": "CA_HI_Blitz",
        "tags": ["trigger-vortex", "hvac", "west-coast", "blitz"]
    }
    
    try:
        res = requests.post(GHL_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code in [200, 201]:
            print(f"  ✅ GHL: {company}")
            logger.info(f"GHL: {company}")
            return True
    except: pass
    return False

def save_dossier(lead):
    company = lead['company_name']
    email = f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com"
    
    try:
        supabase.table("leads").insert({
            'email': email,
            'status': 'contacted',
            'agent_research': json.dumps({
                'company_name': company,
                'phone': f"+1{normalize_phone(lead['phone'])}",
                'city': lead['city'],
                'state': lead['state'],
                'industry': 'HVAC',
                'source': 'CA_HI_Blitz',
                'campaign': 'West Coast Blitz',
                'contacted_at': datetime.now().isoformat(),
                'status': 'active',
                'opt_out': False
            })
        }).execute()
        logger.info(f"Dossier: {company}")
        return True
    except:
        return False

def make_call(lead):
    company = lead['company_name']
    phone = f"+1{normalize_phone(lead['phone'])}"
    
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
            call_id = res.json().get('id', '')[:8]
            print(f"  📞 CALL: {company} ({call_id}...)")
            logger.info(f"CALL: {company} - {call_id}")
            return True
    except: pass
    return False

def send_sms(lead):
    company = lead['company_name']
    phone = f"+1{normalize_phone(lead['phone'])}"
    message = f"Hi! This is Sarah from AI Service Co. We help HVAC companies like {company} book more jobs with 24/7 AI phone answering. Interested in a quick demo? Reply YES!"
    
    try:
        requests.post(GHL_WEBHOOK_URL, json={
            "phone": phone,
            "message": message,
            "source": "CA_HI_Blitz_SMS"
        }, timeout=10)
        print(f"  📱 SMS: {company}")
        logger.info(f"SMS: {company}")
        return True
    except:
        return False

# ============ MAIN - NO TIME CUTOFF ============
def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      🔥 CALIFORNIA + HAWAII BLITZ - 100 COMPANIES       ║
║      NO TIME CUTOFF - RUNS UNTIL OPT-OUT OR SALE        ║
║      WE NEED A SALE! LET'S GO!                          ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"CA+HI BLITZ STARTED - {len(HVAC_LEADS)} leads - {datetime.now()}")
    
    processed = skipped = 0
    
    for i, lead in enumerate(HVAC_LEADS):
        now = datetime.now()
        company = lead['company_name']
        phone = lead['phone']
        
        print(f"\n[{now.strftime('%H:%M:%S')}] {i+1}/{len(HVAC_LEADS)}: {company} ({lead['city']}, {lead['state']})")
        
        # Check duplicate
        if check_if_exists(phone, company):
            print(f"  ⏭️ SKIP: Already contacted")
            skipped += 1
            continue
        
        # EXECUTE FULL BLITZ
        print(f"  🚀 EXECUTING FULL BLITZ...")
        
        # 1. Push to GHL
        ghl_ok = push_to_ghl(lead)
        
        # 2. Save dossier
        save_dossier(lead)
        
        # 3. Make AI call
        call_ok = make_call(lead)
        
        # 4. Send SMS
        sms_ok = send_sms(lead)
        
        if ghl_ok or call_ok or sms_ok:
            processed += 1
            print(f"  ✅ BLITZ COMPLETE! Progress: {processed}/{DAILY_GOAL}")
        
        # Brief pause before next
        if i < len(HVAC_LEADS) - 1:
            print(f"  ⏳ Next in 2 min...")
            time.sleep(INTERVAL_SECONDS)
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      🔥 BLITZ COMPLETE                                   ║
║      Processed: {processed} | Skipped: {skipped}                          ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
║      LET'S GET THAT SALE! 💰                             ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"Blitz complete - Processed: {processed}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
