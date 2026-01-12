"""
🏭 CLOUD PROSPECTOR WITH SALES DOSSIERS
========================================
Runs 24/7 on Modal. Creates detailed sales reports for each prospect.
Better than Apollo - builds complete intelligence profiles.
"""
import modal
import os
import json
import requests
import re
from datetime import datetime, timezone
import anthropic

# Modal App
app = modal.App("empire-prospector-v4")

# Image with all dependencies
prospector_image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "requests", "supabase", "python-dotenv", "anthropic", "pytz"
)

# ============================================================
# PROSPECTOR AGENT - Finds companies continuously
# ============================================================
@app.function(
    image=prospector_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("*/30 * * * *"),  # Every 30 minutes
    timeout=900
)
def cloud_prospector():
    """
    Always-on prospector that finds new leads from multiple sources.
    Runs every 30 minutes in the cloud.
    """
    import os
    import json
    import pytz
    from datetime import datetime
    
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    APOLLO_KEY = os.getenv("APOLLO_API_KEY")
    
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    hour = now.hour
    
    print(f"[PROSPECTOR] Running at {now.strftime('%I:%M %p ET')}")
    
    # Time-based targeting
    if 8 <= hour < 18:
        regions = ["Florida", "Texas", "Georgia", "North Carolina"]
    elif 18 <= hour < 21:
        regions = ["California", "Washington", "Oregon", "Arizona", "Hawaii"]
    else:
        regions = ["Florida", "California", "Texas", "Colorado"]
    
    niches = ["HVAC contractors", "Roofing companies", "Plumbing services"]
    
    new_leads = 0
    for region in regions:
        for niche in niches:
            try:
                resp = requests.post(
                    "https://api.apollo.io/v1/mixed_companies/search",
                    headers={"Content-Type": "application/json"},
                    json={
                        "api_key": APOLLO_KEY,
                        "q_keywords": niche,
                        "organization_locations": [f"{region}, United States"],
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
                        
                        existing = client.table("leads").select("id").eq("company_name", company).execute()
                        if existing.data:
                            continue
                        
                        client.table("leads").insert({
                            "company_name": company,
                            "website": org.get("website_url"),
                            "phone": org.get("phone"),
                            "industry": niche,
                            "city": org.get("city"),
                            "state": org.get("state"),
                            "status": "new",
                            "source": "cloud_prospector"
                        }).execute()
                        new_leads += 1
                        
                elif resp.status_code == 422:
                    print(f"   Apollo rate limit - will retry later")
                    break
            except Exception as e:
                print(f"   Error: {e}")
    
    print(f"[PROSPECTOR] Added {new_leads} new leads")
    return {"new_leads": new_leads}

# ============================================================
# ENRICHER AGENT - Gets decision maker info
# ============================================================
@app.function(
    image=prospector_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("*/20 * * * *"),  # Every 20 minutes
    timeout=900
)
def cloud_enricher():
    """
    Enriches leads with decision maker info from Apollo.
    Gets: Name, Title, Email, Phone, LinkedIn
    """
    import os
    import json
    
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    APOLLO_KEY = os.getenv("APOLLO_API_KEY")
    
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("[ENRICHER] Starting enrichment run...")
    
    # Get leads needing enrichment
    leads = client.table("leads").select("*").eq("status", "new").limit(30).execute()
    
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
                    "person_titles": ["Owner", "CEO", "President", "General Manager", "Operations Manager"],
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
                    
                    client.table("leads").update({
                        "status": "enriched",
                        "email": enrichment.get("enriched_email", ""),
                        "agent_research": json.dumps(enrichment)
                    }).eq("id", lead["id"]).execute()
                    
                    enriched += 1
                    print(f"   ✅ {company} → {person.get('name')}")
                else:
                    client.table("leads").update({"status": "no_contact"}).eq("id", lead["id"]).execute()
            elif resp.status_code == 422:
                print("   Apollo rate limit hit")
                break
        except Exception as e:
            print(f"   Error: {e}")
    
    print(f"[ENRICHER] Enriched {enriched} leads")
    return {"enriched": enriched}

# ============================================================
# DOSSIER BUILDER - Creates detailed sales reports
# ============================================================
@app.function(
    image=prospector_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 */2 * * *"),  # Every 2 hours
    timeout=1200
)
def dossier_builder():
    """
    Uses Claude AI to build comprehensive sales dossiers for each lead.
    Creates reports better than Apollo with competitive intel.
    """
    import os
    import json
    import anthropic
    
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("[DOSSIER] Building sales intelligence reports...")
    
    # Get enriched leads without dossiers
    leads = client.table("leads").select("*").eq("status", "enriched").is_("sales_dossier", "null").limit(10).execute()
    
    print(f"[DOSSIER] Found {len(leads.data)} leads needing dossiers")
    
    if not ANTHROPIC_KEY:
        print("[DOSSIER] No Anthropic key - skipping")
        return {"dossiers": 0}
    
    claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    dossiers_created = 0
    
    for lead in leads.data:
        company = lead.get("company_name", "")
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        
        decision_maker = meta.get("decision_maker", "")
        title = meta.get("title", "")
        city = lead.get("city", "")
        state = lead.get("state", "")
        industry = lead.get("industry", "")
        
        prompt = f"""You are a sales intelligence analyst. Create a comprehensive sales dossier for this prospect:

COMPANY: {company}
DECISION MAKER: {decision_maker} ({title})
LOCATION: {city}, {state}
INDUSTRY: {industry}

Create a sales dossier with these sections:

## 🎯 QUICK FACTS
- Company size estimate
- Service areas
- Likely revenue range

## 💡 PAIN POINTS
- Based on their industry, list 3-5 likely pain points they face
- Focus on challenges AI phone automation could solve

## 🗣️ OPENER SCRIPT
Write a 2-3 sentence personalized call opener for our sales rep to use.
Reference something specific about their business or location.

## 🔥 VALUE PROPS
List 3 specific benefits of AI phone automation for their business:
- 24/7 availability
- Never miss a lead
- Save on staffing

## ⚠️ OBJECTION HANDLERS
Prepare responses for these common objections:
1. "We're too busy"
2. "AI can't handle our calls"
3. "Too expensive"

## 📞 CALL STRATEGY
- Best time to call (based on location timezone)
- Suggested approach

Keep total response under 400 words. Be specific and actionable."""

        try:
            response = claude.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            
            dossier = response.content[0].text
            
            # Save dossier to lead
            client.table("leads").update({
                "sales_dossier": dossier,
                "status": "ready_to_call"
            }).eq("id", lead["id"]).execute()
            
            dossiers_created += 1
            print(f"   ✅ {company} - dossier created")
            
        except Exception as e:
            print(f"   ❌ {company}: {e}")
    
    print(f"[DOSSIER] Created {dossiers_created} sales dossiers")
    return {"dossiers": dossiers_created}

# ============================================================
# CONTACTOR AGENT - Reaches out to ready leads
# ============================================================
@app.function(
    image=prospector_image,
    secrets=[modal.Secret.from_dotenv()],
    schedule=modal.Cron("0 9-17 * * 1-5"),  # Hourly 9 AM - 5 PM Mon-Fri
    timeout=900
)
def cloud_contactor():
    """
    Contacts leads that have dossiers ready.
    Multi-channel: Vapi calls, SMS, Email
    """
    import os
    import json
    import re
    
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
    VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
    RESEND_KEY = os.getenv("RESEND_API_KEY")
    GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
    
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("[CONTACTOR] Starting outreach...")
    
    # Get leads ready to call
    leads = client.table("leads").select("*").eq("status", "ready_to_call").limit(15).execute()
    
    print(f"[CONTACTOR] Found {len(leads.data)} leads ready for contact")
    
    stats = {"calls": 0, "sms": 0, "emails": 0}
    
    for lead in leads.data:
        company = lead.get("company_name", "Business")
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        
        decision_maker = meta.get("decision_maker")
        email = meta.get("enriched_email") or lead.get("email")
        phone = meta.get("enriched_phone") or lead.get("phone")
        
        # Validate phone
        if phone:
            cleaned = re.sub(r'\D', '', str(phone))
            if len(cleaned) >= 10 and cleaned[-7:-4] != "555":
                clean_phone = f"+1{cleaned[-10:]}"
                
                # Make call
                try:
                    resp = requests.post(
                        "https://api.vapi.ai/call",
                        headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
                        json={
                            "type": "outboundPhoneCall",
                            "phoneNumberId": VAPI_PHONE_ID,
                            "assistantId": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a",
                            "customer": {"number": clean_phone, "name": decision_maker or company}
                        },
                        timeout=30
                    )
                    if resp.status_code in [200, 201]:
                        stats["calls"] += 1
                except:
                    pass
                
                # Send SMS
                try:
                    name = decision_maker.split()[0] if decision_maker else "there"
                    msg = f"Hi {name}! Daniel from AI Service Co. We help {company} automate customer calls with AI. Worth a quick chat? 352-758-5336"
                    resp = requests.post(GHL_SMS, json={"phone": clean_phone, "message": msg}, timeout=15)
                    if resp.status_code in [200, 201]:
                        stats["sms"] += 1
                except:
                    pass
        
        # Send email
        if email and "@" in str(email) and RESEND_KEY:
            try:
                name = decision_maker.split()[0] if decision_maker else "there"
                resp = requests.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_KEY}"},
                    json={
                        "from": "Daniel <daniel@aiserviceco.com>",
                        "to": [email],
                        "subject": f"Quick question about {company}",
                        "html": f"<p>Hi {name},</p><p>I help service businesses like {company} automate their phone operations with AI - 24/7 coverage, never miss a call.</p><p>Worth a 5-min chat to see if it could help you?</p><p>Best,<br>Daniel<br>(352) 758-5336</p>"
                    },
                    timeout=15
                )
                if resp.status_code in [200, 201]:
                    stats["emails"] += 1
            except:
                pass
        
        # Update status
        client.table("leads").update({"status": "contacted"}).eq("id", lead["id"]).execute()
    
    print(f"[CONTACTOR] Calls: {stats['calls']}, SMS: {stats['sms']}, Emails: {stats['emails']}")
    return stats

# ============================================================
# HEALTH CHECK
# ============================================================
@app.function(image=prospector_image, secrets=[modal.Secret.from_dotenv()])
@modal.web_endpoint(method="GET")
def system_health():
    """Health check endpoint"""
    import os
    import pytz
    from datetime import datetime
    
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    
    # Get pipeline stats
    total = len(client.table("leads").select("id").execute().data)
    enriched = len(client.table("leads").select("id").eq("status", "enriched").execute().data)
    ready = len(client.table("leads").select("id").eq("status", "ready_to_call").execute().data)
    contacted = len(client.table("leads").select("id").eq("status", "contacted").execute().data)
    
    return {
        "status": "operational",
        "time": now.strftime("%Y-%m-%d %I:%M %p ET"),
        "pipeline": {
            "total_leads": total,
            "enriched": enriched,
            "ready_to_call": ready,
            "contacted": contacted
        },
        "agents": {
            "prospector": "Every 30 min",
            "enricher": "Every 20 min",
            "dossier_builder": "Every 2 hours",
            "contactor": "Hourly 9AM-5PM Mon-Fri"
        }
    }
