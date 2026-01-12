"""
🚀🔥 MEGA TURBO BLITZ - AUTONOMOUS EXECUTION 🔥🚀
Contact 15 people NOW + Enrich 100 new leads
"""
import os
import json
import requests
import re
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
load_dotenv()

# === CREDENTIALS ===
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
APOLLO_KEY = os.getenv("APOLLO_API_KEY")
RESEND_KEY = os.getenv("RESEND_API_KEY")
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === APOLLO ENRICHMENT ===
def apollo_people_search(company_name, domain=None):
    """Find decision makers via Apollo.io"""
    if not APOLLO_KEY:
        return None
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": APOLLO_KEY,
                "q_organization_name": company_name,
                "person_titles": ["Owner", "CEO", "President", "General Manager", "Operations Manager"],
                "per_page": 3
            },
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            people = data.get("people", [])
            if people:
                person = people[0]
                return {
                    "decision_maker": person.get("name"),
                    "title": person.get("title"),
                    "enriched_email": person.get("email"),
                    "enriched_phone": person.get("phone_numbers", [{}])[0].get("sanitized_number") if person.get("phone_numbers") else None,
                    "linkedin_url": person.get("linkedin_url")
                }
    except Exception as e:
        print(f"   Apollo error: {e}")
    return None

def apollo_org_search(keywords, locations, per_page=25):
    """Search for companies via Apollo"""
    if not APOLLO_KEY:
        return []
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/mixed_companies/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": APOLLO_KEY,
                "q_keywords": keywords,
                "organization_locations": locations,
                "per_page": per_page,
                "organization_num_employees_ranges": ["1,10", "11,50", "51,100"]
            },
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get("organizations", [])
    except Exception as e:
        print(f"Apollo org error: {e}")
    return []

# === CONTACT FUNCTIONS ===
def validate_phone(phone_str):
    if not phone_str:
        return False, None
    cleaned = re.sub(r'\D', '', str(phone_str))
    if len(cleaned) < 10:
        return False, None
    if cleaned[-7:-4] == "555":
        return False, None
    return True, f"+1{cleaned[-10:]}"

def make_vapi_call(phone, company, decision_maker=None):
    """Outbound call via Vapi"""
    try:
        name = decision_maker or company
        resp = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": VAPI_PHONE_ID,
                "assistantId": SARAH_ASSISTANT_ID,
                "customer": {"number": phone, "name": name}
            },
            timeout=30
        )
        return resp.status_code in [200, 201]
    except:
        return False

def send_sms(phone, company, decision_maker=None):
    """SMS via GHL"""
    try:
        name = decision_maker.split()[0] if decision_maker else "there"
        msg = f"Hi {name}! This is Daniel from AI Service Co. I help businesses like {company} automate customer calls with AI - 24/7 coverage, no missed calls. Worth a quick chat? Reply or call 352-758-5336"
        resp = requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": msg}, timeout=15)
        return resp.status_code in [200, 201]
    except:
        return False

def send_email(email, company, decision_maker=None):
    """Email via Resend"""
    if not RESEND_KEY or not email or "@" not in str(email):
        return False
    try:
        name = decision_maker.split()[0] if decision_maker else "there"
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_KEY}"},
            json={
                "from": "Daniel <daniel@aiserviceco.com>",
                "to": [email],
                "subject": f"AI phone automation for {company}?",
                "html": f"""<p>Hi {name},</p>
                <p>I came across {company} and thought you might be interested in what we're building at AI Service Co.</p>
                <p>We help service businesses automate their phone operations with AI:</p>
                <ul>
                    <li>24/7 AI receptionist that never misses a call</li>
                    <li>Instant appointment booking</li>
                    <li>Lead qualification on autopilot</li>
                </ul>
                <p>Would love to show you a quick demo. Are you available for a 5-minute call this week?</p>
                <p>Best,<br>Daniel<br>AI Service Co<br>(352) 758-5336</p>"""
            },
            timeout=15
        )
        return resp.status_code in [200, 201]
    except:
        return False

# === MAIN EXECUTION ===
def main():
    print("="*70)
    print("🚀🔥 MEGA TURBO BLITZ - AUTONOMOUS EXECUTION 🔥🚀")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%I:%M %p ET')}")
    print()
    
    # === PHASE 1: PROSPECT 100 NEW LEADS ===
    print("📡 PHASE 1: PROSPECTING 100 NEW LEADS VIA APOLLO...")
    print("-"*70)
    
    niches = [
        ("HVAC contractors", ["Florida, United States", "Texas, United States", "California, United States"]),
        ("Roofing companies", ["Florida, United States", "Georgia, United States", "Arizona, United States"]),
        ("Plumbing services", ["Florida, United States", "Texas, United States", "North Carolina, United States"]),
        ("Electrical contractors", ["Florida, United States", "Tennessee, United States", "Ohio, United States"])
    ]
    
    new_leads = []
    for keywords, locations in niches:
        print(f"   🔍 Searching: {keywords}...")
        orgs = apollo_org_search(keywords, locations, per_page=30)
        for org in orgs:
            new_leads.append({
                "company_name": org.get("name"),
                "website": org.get("website_url"),
                "phone": org.get("phone"),
                "industry": keywords,
                "city": org.get("city"),
                "state": org.get("state"),
                "source": "apollo_turbo_blitz"
            })
        print(f"      Found {len(orgs)} companies")
        time.sleep(1)  # Rate limit
    
    print(f"\n✅ Total new prospects found: {len(new_leads)}")
    
    # === PHASE 2: ENRICH WITH DECISION MAKERS ===
    print("\n🔬 PHASE 2: ENRICHING WITH DECISION MAKERS...")
    print("-"*70)
    
    enriched = 0
    for i, lead in enumerate(new_leads[:100]):
        company = lead.get("company_name", "")
        if not company:
            continue
        
        # Check if already exists
        existing = client.table("leads").select("id").eq("company_name", company).execute()
        if existing.data:
            continue
        
        # Enrich via Apollo
        enrichment = apollo_people_search(company)
        if enrichment:
            lead["agent_research"] = json.dumps(enrichment)
            lead["email"] = enrichment.get("enriched_email", "")
            if enrichment.get("enriched_phone"):
                lead["phone"] = enrichment["enriched_phone"]
            enriched += 1
            print(f"   ✅ [{enriched}] {company} → {enrichment.get('decision_maker', 'N/A')} ({enrichment.get('title', 'N/A')[:30]})")
        
        # Insert into Supabase
        try:
            lead["status"] = "enriched" if enrichment else "new"
            client.table("leads").insert(lead).execute()
        except Exception as e:
            pass
        
        if enriched >= 100:
            break
        time.sleep(0.5)  # Rate limit
    
    print(f"\n✅ Total enriched leads: {enriched}")
    
    # === PHASE 3: CONTACT 15 PEOPLE NOW ===
    print("\n📞 PHASE 3: CONTACTING 15 LEADS NOW...")
    print("-"*70)
    
    # Get ready-to-contact leads
    leads_to_contact = client.table("leads").select("*").in_("status", ["enriched", "new", "processing_email"]).limit(20).execute()
    
    stats = {"calls": 0, "sms": 0, "emails": 0, "contacted": 0}
    
    for lead in leads_to_contact.data:
        if stats["contacted"] >= 15:
            break
        
        company = lead.get("company_name", "Business")
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        if not isinstance(meta, dict):
            meta = {}
        
        decision_maker = meta.get("decision_maker")
        email = meta.get("enriched_email") or lead.get("email")
        phone = meta.get("enriched_phone") or lead.get("phone")
        
        is_valid, clean_phone = validate_phone(phone)
        
        print(f"\n[{stats['contacted']+1}/15] {company}")
        print(f"         👤 {decision_maker or 'Unknown'}")
        print(f"         📞 {clean_phone or 'No phone'} | 📧 {(email or 'No email')[:25]}")
        
        contacted = False
        
        # Call if valid phone
        if is_valid and clean_phone:
            if make_vapi_call(clean_phone, company, decision_maker):
                stats["calls"] += 1
                print(f"         ✅ CALL initiated!")
                contacted = True
                time.sleep(3)  # Space out calls
            
            if send_sms(clean_phone, company, decision_maker):
                stats["sms"] += 1
                print(f"         ✅ SMS sent!")
                contacted = True
        
        # Email
        if email and "@" in str(email):
            if send_email(email, company, decision_maker):
                stats["emails"] += 1
                print(f"         ✅ EMAIL sent!")
                contacted = True
        
        if contacted:
            stats["contacted"] += 1
            try:
                client.table("leads").update({"status": "contacted"}).eq("id", lead["id"]).execute()
            except:
                pass
        
        time.sleep(1)
    
    # === FINAL REPORT ===
    print("\n" + "="*70)
    print("🏁 TURBO BLITZ COMPLETE!")
    print("="*70)
    print(f"📊 NEW LEADS PROSPECTED: {len(new_leads)}")
    print(f"🔬 LEADS ENRICHED: {enriched}")
    print(f"📞 CALLS MADE: {stats['calls']}")
    print(f"💬 SMS SENT: {stats['sms']}")
    print(f"📧 EMAILS SENT: {stats['emails']}")
    print(f"✅ TOTAL CONTACTED: {stats['contacted']}")
    print("="*70)
    print("🚀 SYSTEM IS NOW AUTONOMOUS - Modal will continue 24/7!")
    print("="*70)

if __name__ == "__main__":
    main()
