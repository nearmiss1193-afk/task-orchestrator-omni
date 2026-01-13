"""
🔥 CONTINUOUS AGENT SWARM - NEVER STOPS
========================================
Runs locally in a loop. Prospects, enriches, and contacts continuously.
When cloud rests, this picks up. When this rests, cloud picks up.
TRUE 24/7 OPERATION.
"""
import os
import json
import requests
import re
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
load_dotenv()

# === CREDENTIALS ===
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
RESEND_KEY = os.getenv("RESEND_API_KEY")
APOLLO_KEY = os.getenv("APOLLO_API_KEY")
GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === TIME ZONE TARGETING ===
def get_active_regions():
    """Returns regions where it's currently business hours"""
    hour = datetime.now().hour
    
    # ET hour to region mapping
    if 8 <= hour < 18:  # 8 AM - 6 PM ET
        return ["Florida", "Georgia", "North Carolina", "Texas", "Illinois"]
    elif 18 <= hour < 21:  # 6-9 PM ET = 3-6 PM PT
        return ["California", "Washington", "Oregon", "Arizona", "Hawaii"]
    else:  # Off hours - prep for next day
        return ["California", "Hawaii", "Florida", "Texas"]

# === AGENT 1: PROSPECTOR ===
def prospect_agent():
    """Finds new leads from Apollo"""
    print(f"\n🔍 [PROSPECTOR] Starting search...")
    
    regions = get_active_regions()
    niches = ["HVAC contractors", "Roofing companies", "Plumbing services"]
    
    new_leads = 0
    for region in regions[:2]:  # Process 2 regions per cycle
        for niche in niches[:2]:  # 2 niches per region
            try:
                resp = requests.post(
                    "https://api.apollo.io/v1/mixed_companies/search",
                    headers={"Content-Type": "application/json"},
                    json={
                        "api_key": APOLLO_KEY,
                        "q_keywords": niche,
                        "organization_locations": [f"{region}, United States"],
                        "per_page": 15,
                        "organization_num_employees_ranges": ["1,10", "11,50", "51,100"]
                    },
                    timeout=30
                )
                if resp.status_code == 200:
                    orgs = resp.json().get("organizations", [])
                    for org in orgs:
                        company = org.get("name", "")
                        if not company:
                            continue
                        
                        # Check if exists
                        try:
                            existing = client.table("leads").select("id").eq("company_name", company).execute()
                            if existing.data:
                                continue
                        except:
                            continue
                        
                        # Insert
                        try:
                            client.table("leads").insert({
                                "company_name": company,
                                "phone": org.get("phone"),
                                "website": org.get("website_url"),
                                "city": org.get("city"),
                                "state": org.get("state"),
                                "industry": niche,
                                "status": "new",
                                "source": "swarm_prospector"
                            }).execute()
                            new_leads += 1
                        except:
                            pass
                    print(f"   ✅ {region}/{niche}: {len(orgs)} found, {new_leads} new")
                elif resp.status_code == 422:
                    print(f"   ⚠️ Apollo rate limit - backing off")
                    time.sleep(60)  # Wait 1 minute
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print(f"🔍 [PROSPECTOR] Added {new_leads} new leads")
    return new_leads

# === AGENT 2: ENRICHER ===
def enrich_agent():
    """Enriches leads with decision maker info - uses Apollo + Lusha fallback"""
    print(f"\n🔬 [ENRICHER] Starting enrichment...")
    
    # Import Lusha for fallback
    try:
        from modules.lusha_enricher import lusha, enrich_with_lusha
        lusha_available = True
    except:
        lusha_available = False
        print("   ⚠️ Lusha not available")
    
    # Get leads needing enrichment
    try:
        leads = client.table("leads").select("*").eq("status", "new").limit(10).execute()
    except:
        return 0
    
    enriched = 0
    for lead in leads.data:
        company = lead.get("company_name", "")
        if not company:
            continue
        
        # Try Apollo first
        apollo_success = False
        try:
            resp = requests.post(
                "https://api.apollo.io/v1/mixed_people/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": APOLLO_KEY,
                    "q_organization_name": company,
                    "person_titles": ["Owner", "CEO", "President", "General Manager"],
                    "per_page": 1
                },
                timeout=30
            )
            if resp.status_code == 200:
                people = resp.json().get("people", [])
                if people:
                    p = people[0]
                    enrichment = {
                        "decision_maker": p.get("name"),
                        "title": p.get("title"),
                        "enriched_email": p.get("email"),
                        "enriched_phone": p.get("phone_numbers", [{}])[0].get("sanitized_number") if p.get("phone_numbers") else None,
                        "source": "apollo"
                    }
                    
                    client.table("leads").update({
                        "status": "enriched",
                        "email": enrichment.get("enriched_email", ""),
                        "agent_research": json.dumps(enrichment)
                    }).eq("id", lead["id"]).execute()
                    
                    enriched += 1
                    apollo_success = True
                    print(f"   ✅ {company} → {p.get('name')} (Apollo)")
            elif resp.status_code == 422:
                print(f"   ⚠️ Apollo rate limit")
                time.sleep(30)
        except Exception as e:
            print(f"   ⚠️ Apollo error: {e}")
        
        # LUSHA FALLBACK - if Apollo failed or rate limited
        if not apollo_success and lusha_available:
            try:
                # Try to get any name from the lead
                first_name = lead.get("contact_name", "").split()[0] if lead.get("contact_name") else ""
                last_name = lead.get("contact_name", "").split()[-1] if lead.get("contact_name") and len(lead.get("contact_name", "").split()) > 1 else ""
                
                # If we have no name, try a generic enrichment
                if not first_name:
                    # Try company enrichment first
                    website = lead.get("website", "")
                    if website:
                        domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
                        company_data = lusha.enrich_company(domain)
                        if company_data:
                            print(f"   ✅ {company} company data (Lusha)")
                else:
                    result = lusha.enrich_person(first_name, last_name, company, "both")
                    if result and (result.get("email") or result.get("phone")):
                        enrichment = {
                            "decision_maker": f"{first_name} {last_name}",
                            "enriched_email": result.get("email"),
                            "enriched_phone": result.get("phone"),
                            "lusha_linkedin": result.get("linkedin"),
                            "source": "lusha"
                        }
                        
                        client.table("leads").update({
                            "status": "enriched",
                            "email": enrichment.get("enriched_email", ""),
                            "agent_research": json.dumps(enrichment)
                        }).eq("id", lead["id"]).execute()
                        
                        enriched += 1
                        print(f"   ✅ {company} → {first_name} {last_name} (Lusha)")
            except Exception as e:
                print(f"   ⚠️ Lusha error: {e}")
        
        # If both failed, mark as no_contact
        if not apollo_success and not lusha_available:
            client.table("leads").update({"status": "no_contact"}).eq("id", lead["id"]).execute()
    
    print(f"🔬 [ENRICHER] Enriched {enriched} leads")
    return enriched

# === AGENT 3: CONTACTOR ===
def validate_phone(phone_str):
    if not phone_str:
        return False, None
    cleaned = re.sub(r'\D', '', str(phone_str))
    if len(cleaned) < 10 or cleaned[-7:-4] == "555":
        return False, None
    return True, f"+1{cleaned[-10:]}"

def contact_agent():
    """Contacts enriched leads via call, SMS, email"""
    print(f"\n📞 [CONTACTOR] Starting outreach...")
    
    # Get enriched leads
    try:
        leads = client.table("leads").select("*").eq("status", "enriched").limit(5).execute()
    except:
        return {"calls": 0, "sms": 0, "emails": 0}
    
    stats = {"calls": 0, "sms": 0, "emails": 0}
    
    for lead in leads.data:
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
        
        print(f"\n   📍 {company}")
        print(f"      👤 {decision_maker or 'Unknown'}")
        
        # CALL
        if is_valid and clean_phone:
            try:
                resp = requests.post(
                    "https://api.vapi.ai/call",
                    headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
                    json={
                        "type": "outboundPhoneCall",
                        "phoneNumberId": VAPI_PHONE_ID,
                        "assistantId": SARAH_ID,
                        "customer": {"number": clean_phone, "name": decision_maker or company}
                    },
                    timeout=30
                )
                if resp.status_code in [200, 201]:
                    stats["calls"] += 1
                    print(f"      ✅ CALL → {clean_phone}")
            except:
                pass
            
            # SMS
            try:
                name = decision_maker.split()[0] if decision_maker else "there"
                msg = f"Hi {name}! Daniel from AI Service Co. We help {company} automate calls with AI - 24/7 coverage. Worth a chat? 352-758-5336"
                resp = requests.post(GHL_SMS, json={"phone": clean_phone, "message": msg}, timeout=15)
                if resp.status_code in [200, 201]:
                    stats["sms"] += 1
                    print(f"      ✅ SMS sent")
            except:
                pass
        
        # EMAIL
        if email and "@" in str(email):
            try:
                name = decision_maker.split()[0] if decision_maker else "there"
                resp = requests.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_KEY}"},
                    json={
                        "from": "Daniel <daniel@aiserviceco.com>",
                        "to": [email],
                        "subject": f"Quick question for {company}",
                        "html": f"<p>Hi {name},</p><p>I help service businesses like {company} automate their phone operations with AI - 24/7 coverage, never miss a call.</p><p>Worth a 5-min chat?</p><p>Best,<br>Daniel<br>(352) 758-5336</p>"
                    },
                    timeout=15
                )
                if resp.status_code in [200, 201]:
                    stats["emails"] += 1
                    print(f"      ✅ EMAIL sent")
            except:
                pass
        
        # Update status
        try:
            client.table("leads").update({"status": "contacted"}).eq("id", lead["id"]).execute()
        except:
            pass
    
    print(f"📞 [CONTACTOR] Calls: {stats['calls']}, SMS: {stats['sms']}, Emails: {stats['emails']}")
    return stats

# === MAIN SWARM LOOP ===
def main():
    print("="*60)
    print("🔥 CONTINUOUS AGENT SWARM - NEVER STOPS 🔥")
    print("="*60)
    print("Press Ctrl+C to stop")
    print()
    
    cycle = 0
    total_stats = {"prospected": 0, "enriched": 0, "calls": 0, "sms": 0, "emails": 0}
    
    while True:
        cycle += 1
        print(f"\n{'='*60}")
        print(f"⚡ CYCLE {cycle} - {datetime.now().strftime('%I:%M %p ET')}")
        print(f"{'='*60}")
        
        # Run all agents in sequence
        try:
            # 1. Prospect
            new = prospect_agent()
            total_stats["prospected"] += new
            time.sleep(2)
            
            # 2. Enrich
            enriched = enrich_agent()
            total_stats["enriched"] += enriched
            time.sleep(2)
            
            # 3. Contact
            contact_stats = contact_agent()
            total_stats["calls"] += contact_stats["calls"]
            total_stats["sms"] += contact_stats["sms"]
            total_stats["emails"] += contact_stats["emails"]
            
        except KeyboardInterrupt:
            print("\n\n🛑 SWARM STOPPED BY USER")
            break
        except Exception as e:
            print(f"❌ Cycle error: {e}")
        
        # Status report
        print(f"\n📊 CUMULATIVE STATS (after {cycle} cycles):")
        print(f"   🔍 Prospected: {total_stats['prospected']}")
        print(f"   🔬 Enriched: {total_stats['enriched']}")
        print(f"   📞 Calls: {total_stats['calls']}")
        print(f"   💬 SMS: {total_stats['sms']}")
        print(f"   📧 Emails: {total_stats['emails']}")
        
        # Wait between cycles (adjustable)
        print(f"\n⏳ Next cycle in 60 seconds...")
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n🛑 SWARM STOPPED BY USER")
            break
    
    print("\n" + "="*60)
    print("🏁 FINAL STATS:")
    print(f"   Cycles completed: {cycle}")
    print(f"   Total prospected: {total_stats['prospected']}")
    print(f"   Total enriched: {total_stats['enriched']}")
    print(f"   Total calls: {total_stats['calls']}")
    print(f"   Total SMS: {total_stats['sms']}")
    print(f"   Total emails: {total_stats['emails']}")
    print("="*60)

if __name__ == "__main__":
    main()
