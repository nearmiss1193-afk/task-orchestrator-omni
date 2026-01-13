"""
🌅 WEST COAST EVENING BLITZ
===========================
7:27 PM ET = 4:27 PM PT = 2:27 PM HT
PRIME TIME for California, Washington, Oregon, Hawaii, Arizona!
"""
import os
import json
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Credentials
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
RESEND_KEY = os.getenv("RESEND_API_KEY")
GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
APOLLO_KEY = os.getenv("APOLLO_API_KEY")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)

WEST_COAST_STATES = ["CA", "WA", "OR", "AZ", "NV", "HI"]

def validate_phone(phone_str):
    if not phone_str:
        return False, None
    cleaned = re.sub(r'\D', '', str(phone_str))
    if len(cleaned) < 10:
        return False, None
    if cleaned[-7:-4] == "555":
        return False, None
    return True, f"+1{cleaned[-10:]}"

def prospect_west_coast():
    """Find new West Coast leads via Apollo"""
    print("🌴 PROSPECTING WEST COAST + HAWAII...")
    
    new_leads = []
    targets = [
        ("HVAC contractors", "California, United States"),
        ("HVAC contractors", "Washington, United States"),
        ("HVAC contractors", "Arizona, United States"),
        ("Roofing companies", "California, United States"),
        ("Plumbing services", "Hawaii, United States"),
    ]
    
    for niche, location in targets:
        try:
            resp = requests.post(
                "https://api.apollo.io/v1/mixed_companies/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": APOLLO_KEY,
                    "q_keywords": niche,
                    "organization_locations": [location],
                    "per_page": 25,
                    "organization_num_employees_ranges": ["1,10", "11,50", "51,100"]
                },
                timeout=30
            )
            if resp.status_code == 200:
                orgs = resp.json().get("organizations", [])
                for org in orgs:
                    new_leads.append({
                        "company_name": org.get("name"),
                        "phone": org.get("phone"),
                        "website": org.get("website_url"),
                        "city": org.get("city"),
                        "state": org.get("state"),
                        "industry": niche,
                        "source": "west_coast_blitz"
                    })
                print(f"   ✅ {location.split(',')[0]}/{niche}: {len(orgs)} found")
            elif resp.status_code == 422:
                print(f"   ⚠️ Apollo rate limit")
                break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return new_leads

def enrich_lead(company_name):
    """Get decision maker from Apollo"""
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": APOLLO_KEY,
                "q_organization_name": company_name,
                "person_titles": ["Owner", "CEO", "President", "General Manager"],
                "per_page": 1
            },
            timeout=30
        )
        if resp.status_code == 200:
            people = resp.json().get("people", [])
            if people:
                p = people[0]
                return {
                    "decision_maker": p.get("name"),
                    "title": p.get("title"),
                    "enriched_email": p.get("email"),
                    "enriched_phone": p.get("phone_numbers", [{}])[0].get("sanitized_number") if p.get("phone_numbers") else None
                }
    except:
        pass
    return None

def main():
    print("="*60)
    print("🌅 WEST COAST EVENING BLITZ")
    print("="*60)
    print(f"Current Time: 7:27 PM ET = 4:27 PM PT = 2:27 PM HT")
    print("Target: California, Washington, Oregon, Arizona, Hawaii")
    print()
    
    stats = {"prospected": 0, "enriched": 0, "calls": 0, "sms": 0, "emails": 0}
    
    # Phase 1: Prospect
    new_leads = prospect_west_coast()
    stats["prospected"] = len(new_leads)
    print(f"\n📊 Found {len(new_leads)} West Coast prospects")
    
    # Phase 2: Enrich and Contact
    print("\n📞 CONTACTING WEST COAST LEADS...")
    print("-"*60)
    
    contacted = 0
    for lead in new_leads[:20]:  # Contact first 20
        company = lead.get("company_name", "")
        if not company:
            continue
        
        # Check if exists
        try:
            existing = client.table("leads").select("id").eq("company_name", company).execute()
            if existing.data:
                continue
        except:
            pass
        
        # Enrich
        enrichment = enrich_lead(company)
        if enrichment:
            lead["agent_research"] = json.dumps(enrichment)
            lead["email"] = enrichment.get("enriched_email")
            lead["status"] = "enriched"
            stats["enriched"] += 1
        else:
            lead["status"] = "new"
        
        # Insert
        try:
            result = client.table("leads").insert(lead).execute()
            lead_id = result.data[0]["id"] if result.data else None
        except:
            continue
        
        # Contact
        phone = enrichment.get("enriched_phone") if enrichment else lead.get("phone")
        email = lead.get("email")
        decision_maker = enrichment.get("decision_maker") if enrichment else None
        
        is_valid, clean_phone = validate_phone(phone)
        
        print(f"\n[{contacted+1}] {company}")
        print(f"     👤 {decision_maker or 'Unknown'}")
        
        # Call
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
                    print(f"     ✅ CALL → {clean_phone}")
            except:
                pass
            
            # SMS
            try:
                name = decision_maker.split()[0] if decision_maker else "there"
                msg = f"Hi {name}! Daniel from AI Service Co. We help businesses like {company} automate customer calls with AI - 24/7 coverage. Worth a quick chat? 352-758-5336"
                resp = requests.post(GHL_SMS, json={"phone": clean_phone, "message": msg}, timeout=15)
                if resp.status_code in [200, 201]:
                    stats["sms"] += 1
                    print(f"     ✅ SMS sent")
            except:
                pass
        
        # Email
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
                        "html": f"<p>Hi {name},</p><p>I help service businesses like {company} automate their phone operations with AI.</p><p>Would 24/7 coverage that never misses a call be valuable for you?</p><p>Worth a 5-min chat?</p><p>Best,<br>Daniel<br>(352) 758-5336</p>"
                    },
                    timeout=15
                )
                if resp.status_code in [200, 201]:
                    stats["emails"] += 1
                    print(f"     ✅ EMAIL sent")
            except:
                pass
        
        # Update status
        try:
            client.table("leads").update({"status": "contacted"}).eq("id", lead_id).execute()
        except:
            pass
        
        contacted += 1
    
    # Report
    print("\n" + "="*60)
    print("🏁 WEST COAST BLITZ COMPLETE!")
    print("="*60)
    print(f"📊 RESULTS:")
    print(f"   🌴 Prospected: {stats['prospected']}")
    print(f"   🔬 Enriched: {stats['enriched']}")
    print(f"   📞 Calls: {stats['calls']}")
    print(f"   💬 SMS: {stats['sms']}")
    print(f"   📧 Emails: {stats['emails']}")
    print()
    print("TONIGHT PROJECTIONS (until 9 PM PT / 12 AM ET):")
    print("   🌙 Remaining Hours: ~5 hours")
    print("   📞 Projected Calls: 50-75")
    print("   💬 Projected SMS: 50+")
    print("   📧 Projected Emails: 100+")
    print("="*60)

if __name__ == "__main__":
    main()
