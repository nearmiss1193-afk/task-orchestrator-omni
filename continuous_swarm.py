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
GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"


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
def prospect_agent(niche_strategy=None):
    """Finds new leads from Apollo"""
    print(f"\n🔍 [PROSPECTOR] Starting search...")
    
    regions = get_active_regions()
    niches = ["HVAC contractors", "Roofing companies", "Plumbing services"]
    
    # Brain Strategy Injection
    if niche_strategy:
        print(f"   🧠 Focusing on STRATEGIC NICHE: {niche_strategy}")
        # Map common names to Apollo keywords if needed
        strategies = {
            "plumber": "Plumbing services",
            "hvac": "HVAC contractors",
            "roofer": "Roofing companies"
        }
        keyword = strategies.get(niche_strategy, niche_strategy)
        niches = [keyword] # Override or prepend? Let's OVERRIDE to focus fire.
    
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

# === AGENT 2.5: AUDITOR (GHL PROSPECTOR) ===
def audit_agent():
    """Generates GHL Deficiency Reports for enriched leads"""
    print(f"\n🕵️ [AUDITOR] Checking for leads to audit...")
    
    # Check if we have credentials
    if not os.getenv("GHL_EMAIL") or not os.getenv("GHL_PASSWORD"):
        print("   ⚠️ Missing GHL_EMAIL/PASSWORD in .env - skipping audit")
        return 0

    try:
        # Get enriched leads that haven't been audited yet
        # Schema change: we need a way to filter. We'll use 'status=enriched'
        # and assume Contactor now looks for 'audited' or 'enriched' (we will change Contactor to prefer audited)
        leads = client.table("leads").select("*").eq("status", "enriched").is_("agent_research->>audit_link", "null").limit(2).execute()
    except:
        return 0

    if not leads.data:
        return 0

    audited_count = 0
    from modules.web.ghl_prospector import GHLProspector
    
    # Initialize Prospector (headless_mode=True usually)
    prospector = GHLProspector(headless=True)
    
    for lead in leads.data:
        company = lead.get("company_name")
        city = lead.get("city") or "Lakeland" # Fallback
        state = lead.get("state") or "FL"
        
        print(f"   🕵️ Auditing: {company}...")
        
        try:
            # Generate Report
            # We combine city/state for the search query
            location_str = f"{city}, {state}"
            report_link = prospector.generate_report(company, location_str)
            
            if report_link:
                # Update Lead
                # We store the link in agent_research JSON
                meta = lead.get("agent_research") or {}
                if isinstance(meta, str): meta = json.loads(meta)
                
                meta["audit_link"] = report_link
                meta["audit_date"] = datetime.now().isoformat()
                
                client.table("leads").update({
                    "status": "audited", # New status
                    "agent_research": json.dumps(meta)
                }).eq("id", lead["id"]).execute()
                
                print(f"   ✅ Report Generated: {report_link}")
                audited_count += 1
            else:
                print(f"   ⚠️ Failed to generate report")
                # Mark as 'skipped_audit' so we don't loop forever? 
                # Or just leave as enriched and let Contactor pick it up without audit (need to ensure Contactor handles both)
                pass

        except Exception as e:
            print(f"   ❌ Audit Error: {e}")

    return audited_count


# === AGENT 3: CONTACTOR ===
# Tracking globals
last_call_time = 0

def validate_phone(phone_str):
    if not phone_str:
        return False, None
    cleaned = re.sub(r'\D', '', str(phone_str))
    if len(cleaned) < 10 or cleaned[-7:-4] == "555":
        return False, None
    return True, f"+1{cleaned[-10:]}"

def contact_agent():
    """Contacts enriched leads via call, SMS, email"""
    global last_call_time
    print(f"\n📞 [CONTACTOR] Starting outreach...")
    
    # Get leads to contact (prioritize audited, then enriched)
    try:
        # First try Audited
        leads = client.table("leads").select("*").eq("status", "audited").limit(5).execute()
        if not leads.data:
            # Fallback to Enriched
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
        
        # TIME CHECK FOR CALLS
        current_hour = datetime.now().hour
        time_since_last_call = time.time() - last_call_time
        
        # CALL & SMS (Only if after 8 AM and pacing is met)
        if current_hour >= 8:
            if time_since_last_call >= 120: # 2 minutes
                if is_valid and clean_phone:
                    try:
                        print("      📞 Initiating Call...")
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
                            last_call_time = time.time() # Update last call time
                            print(f"      ✅ CALL → {clean_phone}")
                            
                            # SMS FOLLOW-UP
                            try:
                                name = decision_maker.split()[0] if decision_maker else "there"
                                msg = f"Hi {name}! Sarah here from AI Service Co. Just tried calling about automating your phones. We have a free text line for the first 25 partners this month. Chat soon? 352-758-5336"
                                resp = requests.post(GHL_SMS, json={"phone": clean_phone, "message": msg}, timeout=15)
                                if resp.status_code in [200, 201]:
                                    stats["sms"] += 1
                                    print(f"      ✅ SMS sent")
                            except:
                                pass
                                
                    except Exception as e:
                        print(f"      ❌ Call failed: {e}")
            else:
                print(f"      ⏳ Skipping call (pacing: {int(120 - time_since_last_call)}s remaining)")
        else:
            print(f"      ⏳ Skipping call (Before 8 AM)")
        
        # EMAIL (Always send if we have an audit, regardless of time)
        if email and "@" in str(email):
            try:
                audit_link = meta.get("audit_link")
                if not audit_link:
                    print(f"      ⚠️ No Audit Link - SKIPPING EMAIL (SOP Violation)")
                    continue

                name = decision_maker.split()[0] if decision_maker else "there"
                
                # Dynamic Asset Routing
                from modules.learning.brain import EmpireBrain
                brain = EmpireBrain()
                
                # Guess niche from industry or company name
                niche = lead.get("industry", "").lower()
                if not niche:
                     if "roof" in company.lower(): niche = "roofer"
                     elif "pump" in company.lower() or "plumb" in company.lower(): niche = "plumber"
                     elif "air" in company.lower() or "cool" in company.lower(): niche = "hvac"
                     else: niche = "plumber" # Default
                
                assets = brain.get_asset_map(niche)
                video_link = assets.get("video_link", "https://top-local-plumber.vercel.app/#video")
                branding = assets.get("branding", {
                    "sender": "Daniel from AI Service Co",
                    "company": "AI Service Co",
                    "headline": "Stop losing revenue to voicemail and admin work."
                })

                html_body = f"""
                <p>Hi {name},</p>
                
                <p>I ran a specific text-back audit on {company} for our morning review and found some gaps in how you're capturing after-hours leads.</p>
                
                <p><strong><a href="{audit_link}">>> View Your Deficiency Report & ROI Plan</a></strong></p>
                
                <p>We install "Sarah" (our AI Voice Agent) to fix this instantly. She answers calls 24/7, negotiates prices, and books jobs.</p>
                
                <p><strong>Beyond missed calls, we automate your entire back office:</strong></p>
                <ul>
                    <li><strong>TV-Quality Commercials & Ads</strong> - Dominate your local market.</li>
                    <li><strong>Payroll & Office Automation</strong> - Eliminate manual data entry.</li>
                    <li><strong>24/7 Social Monitoring</strong> - Never miss a customer query online.</li>
                </ul>
                
                <p><strong>Use Case for {company}:</strong></p>
                <p>{branding['headline']} Sarah costs less than a single day's pay on our $99/mo plan.</p>
                
                <p><strong>Bonus:</strong> We're giving a <strong style="color: #047857;">Free SMS Text Number</strong> to our first 25 partners this week.</p>
                
                <p>See it in action: <a href="{video_link}">Watch 30s Demo</a></p>
                
                <p>Are you the right person to speak with about this?</p>
                
                <p>Best,<br>
                {branding['sender']}<br>
                {branding['company']}<br>
                (352) 758-5336</p>
                """
                
                
                resp = requests.post(
                    GHL_EMAIL,
                    json={
                        "email": email,
                        "from_name": branding['sender'],
                        "from_email": "daniel@aiserviceco.com",
                        "subject": f"Missed calls at {company}?",
                        "html_body": html_body,
                        "company": company,
                        "audit_link": audit_link
                    },
                    timeout=15
                )
                if resp.status_code in [200, 201]:
                    stats["emails"] += 1
                    print(f"      ✅ EMAIL sent via GHL")
                    
                    # SEND COPY TO OWNER
                    try:
                        requests.post(
                            GHL_EMAIL,
                            json={
                                "email": "owner@aiserviceco.com",
                                "from_name": "Swarm Bot",
                                "from_email": "system@aiserviceco.com",
                                "subject": f"[OUTREACH COPY] {company}",
                                "html_body": f"<p><b>Sent to:</b> {email}</p><hr/>{html_body}",
                                "company": company,
                                "audit_link": audit_link
                            },
                            timeout=10
                        )
                        print(f"      📧 Copy sent to owner")
                    except:
                        pass
                    
                    # Brain Learning Log
                    try:
                        log_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "type": "outreach_success",
                            "company": company,
                            "audit_link": audit_link,
                            "email": email
                        }
                        with open("brain_log.json", "a") as f:
                            f.write(json.dumps(log_entry) + "\n")
                    except:
                        pass
            except:
                print("      ❌ Email failed")
                pass
        
        # Update status
        try:
            client.table("leads").update({"status": "contacted"}).eq("id", lead["id"]).execute()
        except:
            pass
    
    print(f"📞 [CONTACTOR] Calls: {stats['calls']}, SMS: {stats['sms']}, Emails: {stats['emails']}")
    return stats

# === THREADED LOOPS ===
def run_production_loop(stop_event):
    """Loop for Finding, Enriching, and Auditing Leads (The Factory)"""
    print("🏭 [PRODUCTION] Thread started...")
    
    # Initialize The Brain
    from modules.learning.brain import EmpireBrain
    brain = EmpireBrain()
    
    while not stop_event.is_set():
        try:
            # 0. Learn & Optimize
            strategy = brain.reflect_and_optimize()
            target_niche = strategy.get("focus_niche", "plumber")
            print(f"   🧠 Strategy Update: Targeting '{target_niche}'")

            # 1. Prospect
            # Pass the optimized niche to the prospector
            prospect_agent(niche_strategy=target_niche) 
            time.sleep(2)
            
            # 2. Enrich
            enrich_agent()
            time.sleep(2)
            
            # 3. Audit
            audit_agent()
            
            # Rest briefly to avoid hammering APIs
            time.sleep(5)
        except Exception as e:
            print(f"   ❌ Production Loop Error: {e}")
            time.sleep(10)

def run_outreach_loop(stop_event):
    """Loop for contacting leads (The Sales Floor)"""
    print("☎️ [OUTREACH] Thread started...")
    while not stop_event.is_set():
        try:
            contact_agent()
            # Check more frequently than production
            time.sleep(5)
        except Exception as e:
            print(f"   ❌ Outreach Loop Error: {e}")
            time.sleep(10)

# === MAIN SWARM LOOP ===
def main():
    print("="*60)
    print("🔥 CONTINUOUS AGENT SWARM - PARALLEL MODE 🔥")
    print("="*60)
    print("   🏭 Thread 1: Prospecting, Enriching, Auditing")
    print("   ☎️ Thread 2: Calling, SMS, Emailing")
    print("="*60)
    print("Press Ctrl+C to stop")
    print()
    
    stop_event = threading.Event()
    
    # Start Threads
    prod_thread = threading.Thread(target=run_production_loop, args=(stop_event,), daemon=True)
    outreach_thread = threading.Thread(target=run_outreach_loop, args=(stop_event,), daemon=True)
    
    prod_thread.start()
    outreach_thread.start()
    
    try:
        # Main thread just monitors
        while True:
            time.sleep(60)
            print(f"\n✅ SWARM ACTIVE - {datetime.now().strftime('%I:%M %p ET')}")
            
    except KeyboardInterrupt:
        print("\n\n🛑 STOPPING SWARM...")
        stop_event.set()
        # Allow threads a moment to finish current task
        time.sleep(2)
        print("🏁 Swarm Shutdown Complete.")

if __name__ == "__main__":
    main()
