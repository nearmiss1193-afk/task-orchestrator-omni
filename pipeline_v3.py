"""
🏭 PROFESSIONAL PIPELINE ARCHITECTURE
=====================================
3 Parallel Agents:
1. PROSPECTOR - Finds new leads (targets West Coast when East is closed)
2. ENRICHER - Apollo lookups to get decision makers
3. CONTACTOR - SMS/Calls/Emails from enriched queue

Time Zone Aware:
- East Coast (ET): 8 AM - 6 PM for contact
- West Coast (PT): 8 AM - 6 PM = 11 AM - 9 PM ET for prospecting
- Hawaii (HT): 8 AM - 4 PM = 1 PM - 9 PM ET for late prospecting
"""
import modal
import os
import json
import requests
import re
from datetime import datetime, timezone
import pytz

# Modal App
app = modal.App("empire-pipeline-v3")

# Image with dependencies
pipeline_image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "requests", "supabase", "python-dotenv", "pytz", "anthropic"
)

# ========================================================
# AGENT 1: PROSPECTOR (Time-Zone Aware)
# ========================================================
@app.function(
    image=pipeline_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 */2 * * *"),  # Every 2 hours
    timeout=600
)
def prospector_agent():
    """
    Smart prospector that targets regions based on time:
    - 8 AM - 6 PM ET: East Coast leads (ready for immediate contact)
    - 6 PM - 9 PM ET: West Coast + Hawaii leads (prep for tomorrow)
    - 9 PM - 8 AM ET: All regions (batch prep)
    """
    import os
    from datetime import datetime
    import pytz
    
    APOLLO_KEY = os.getenv("APOLLO_API_KEY")
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Determine current time zone targeting
    et = pytz.timezone('US/Eastern')
    now_et = datetime.now(et)
    hour = now_et.hour
    
    print(f"[PROSPECTOR] Running at {now_et.strftime('%I:%M %p ET')}")
    
    # Time-based targeting
    if 8 <= hour < 18:  # Business hours ET
        regions = [
            ("Florida, United States", "HVAC contractors"),
            ("Texas, United States", "Roofing companies"),
            ("Georgia, United States", "Plumbing services"),
            ("North Carolina, United States", "Electrical contractors"),
        ]
        priority = "immediate"
        print(f"[PROSPECTOR] East Coast business hours - targeting for immediate contact")
    elif 18 <= hour < 21:  # 6-9 PM ET = 3-6 PM PT (West Coast prime)
        regions = [
            ("California, United States", "HVAC contractors"),
            ("Washington, United States", "Roofing companies"),
            ("Oregon, United States", "Plumbing services"),
            ("Arizona, United States", "Electrical contractors"),
            ("Hawaii, United States", "HVAC contractors"),
        ]
        priority = "west_coast"
        print(f"[PROSPECTOR] West Coast prime hours - targeting Pacific timezone")
    else:  # Off hours - batch prep
        regions = [
            ("Florida, United States", "HVAC contractors"),
            ("California, United States", "Roofing companies"),
            ("Texas, United States", "Plumbing services"),
            ("Colorado, United States", "Electrical contractors"),
        ]
        priority = "batch"
        print(f"[PROSPECTOR] Off hours - batch prospecting all regions")
    
    # Apollo search
    new_leads = 0
    for location, keywords in regions:
        try:
            resp = requests.post(
                "https://api.apollo.io/v1/mixed_companies/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": APOLLO_KEY,
                    "q_keywords": keywords,
                    "organization_locations": [location],
                    "per_page": 25,
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
                    existing = client.table("leads").select("id").eq("company_name", company).execute()
                    if existing.data:
                        continue
                    
                    # Insert new lead
                    client.table("leads").insert({
                        "company_name": company,
                        "website": org.get("website_url"),
                        "phone": org.get("phone"),
                        "industry": keywords,
                        "city": org.get("city"),
                        "state": org.get("state"),
                        "status": "needs_enrichment",
                        "source": f"apollo_{priority}",
                        "agent_research": json.dumps({"timezone_priority": priority, "location": location})
                    }).execute()
                    new_leads += 1
                    
                print(f"   ✅ {location}/{keywords}: Found {len(orgs)} orgs, added {new_leads} new")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"[PROSPECTOR] Complete! Added {new_leads} new leads")
    return {"new_leads": new_leads, "priority": priority}

# ========================================================
# AGENT 2: ENRICHER (Runs in parallel, processes queue)
# ========================================================
@app.function(
    image=pipeline_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("*/30 * * * *"),  # Every 30 minutes
    timeout=600
)
def enricher_agent():
    """
    Continuously enriches leads with Apollo people search
    Gets: Decision maker name, email, phone, title, LinkedIn
    """
    import os
    import json
    
    APOLLO_KEY = os.getenv("APOLLO_API_KEY")
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print(f"[ENRICHER] Starting enrichment run...")
    
    # Get leads needing enrichment
    leads = client.table("leads").select("*").eq("status", "needs_enrichment").limit(50).execute()
    
    print(f"[ENRICHER] Found {len(leads.data)} leads to enrich")
    
    enriched = 0
    for lead in leads.data:
        company = lead.get("company_name", "")
        if not company:
            continue
        
        try:
            resp = requests.post(
                "https://api.apollo.io/v1/mixed_people/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": APOLLO_KEY,
                    "q_organization_name": company,
                    "person_titles": ["Owner", "CEO", "President", "General Manager", "Operations Manager", "Office Manager"],
                    "per_page": 3
                },
                timeout=30
            )
            if resp.status_code == 200:
                people = resp.json().get("people", [])
                if people:
                    person = people[0]
                    enrichment = {
                        "decision_maker": person.get("name"),
                        "title": person.get("title"),
                        "enriched_email": person.get("email"),
                        "enriched_phone": person.get("phone_numbers", [{}])[0].get("sanitized_number") if person.get("phone_numbers") else None,
                        "linkedin_url": person.get("linkedin_url"),
                        "enriched_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Update lead
                    client.table("leads").update({
                        "status": "enriched",
                        "email": enrichment.get("enriched_email", ""),
                        "agent_research": json.dumps(enrichment)
                    }).eq("id", lead["id"]).execute()
                    
                    enriched += 1
                    print(f"   ✅ {company} → {person.get('name')} ({person.get('title', 'N/A')[:25]})")
                else:
                    # No people found, mark as processed
                    client.table("leads").update({"status": "no_contact_found"}).eq("id", lead["id"]).execute()
        except Exception as e:
            print(f"   ❌ {company}: {e}")
    
    print(f"[ENRICHER] Complete! Enriched {enriched} leads")
    return {"enriched": enriched}

# ========================================================
# AGENT 3: CONTACTOR (Business hours only)
# ========================================================
@app.function(
    image=pipeline_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 8-18 * * 1-6"),  # Hourly 8 AM - 6 PM Mon-Sat
    timeout=900
)
def contactor_agent():
    """
    Contacts enriched leads during business hours
    Multi-channel: Email, SMS, Vapi calls
    """
    import os
    import json
    import re
    import pytz
    
    VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
    VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
    SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
    RESEND_KEY = os.getenv("RESEND_API_KEY")
    GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
    
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    print(f"[CONTACTOR] Running at {now.strftime('%I:%M %p ET')}")
    
    # Get enriched leads ready for contact
    leads = client.table("leads").select("*").eq("status", "enriched").limit(15).execute()
    
    print(f"[CONTACTOR] Found {len(leads.data)} enriched leads to contact")
    
    def validate_phone(phone_str):
        if not phone_str:
            return False, None
        cleaned = re.sub(r'\D', '', str(phone_str))
        if len(cleaned) < 10:
            return False, None
        if cleaned[-7:-4] == "555":
            return False, None
        return True, f"+1{cleaned[-10:]}"
    
    stats = {"calls": 0, "sms": 0, "emails": 0, "total": 0}
    
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
        
        print(f"\n   [{stats['total']+1}] {company}")
        print(f"       👤 {decision_maker or 'Unknown'}")
        
        contacted = False
        
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
                    print(f"       ✅ CALL to {clean_phone}")
                    contacted = True
            except:
                pass
            
            # SMS
            try:
                name = decision_maker.split()[0] if decision_maker else "there"
                msg = f"Hi {name}! Daniel from AI Service Co. We help businesses like {company} automate customer calls with AI. Worth a chat? 352-758-5336"
                resp = requests.post(GHL_SMS, json={"phone": clean_phone, "message": msg}, timeout=15)
                if resp.status_code in [200, 201]:
                    stats["sms"] += 1
                    print(f"       ✅ SMS sent")
                    contacted = True
            except:
                pass
        
        # EMAIL
        if email and "@" in str(email) and RESEND_KEY:
            try:
                name = decision_maker.split()[0] if decision_maker else "there"
                resp = requests.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_KEY}"},
                    json={
                        "from": "Daniel <daniel@aiserviceco.com>",
                        "to": [email],
                        "subject": f"AI phone automation for {company}?",
                        "html": f"<p>Hi {name},</p><p>Quick question - would AI that answers your phones 24/7 help {company}?</p><p>We help service businesses automate customer calls. Worth a 5-min chat?</p><p>Best,<br>Daniel<br>(352) 758-5336</p>"
                    },
                    timeout=15
                )
                if resp.status_code in [200, 201]:
                    stats["emails"] += 1
                    print(f"       ✅ EMAIL sent")
                    contacted = True
            except:
                pass
        
        if contacted:
            stats["total"] += 1
            client.table("leads").update({"status": "contacted"}).eq("id", lead["id"]).execute()
    
    print(f"\n[CONTACTOR] Complete! Calls: {stats['calls']}, SMS: {stats['sms']}, Emails: {stats['emails']}")
    return stats

# ========================================================
# HEALTH CHECK
# ========================================================
@app.function(image=pipeline_image, secrets=[modal.Secret.from_dotenv()])
@modal.web_endpoint(method="GET")
def pipeline_health():
    """Health check endpoint"""
    import pytz
    from datetime import datetime
    
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    
    return {
        "status": "operational",
        "time_et": now.strftime("%Y-%m-%d %I:%M %p ET"),
        "agents": {
            "prospector": "Every 2 hours - timezone-aware",
            "enricher": "Every 30 min - parallel enrichment",
            "contactor": "Hourly 8AM-6PM Mon-Sat"
        }
    }
