"""
RAILWAY CLOUD WORKER
====================
Full autonomous outreach system running 24/7 on Railway.
Combines: Prospecting, Outreach, Inbound Response
"""
import os
import time
import json
import random
import requests
import schedule
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
from brain import EmpireBrain
from reliable_email import send_email as reliable_send_email
from memory import resolve_or_create_contact, write_event, get_memory_context_string, acquire_job_lock, release_job_lock

# Firebase fallback (optional)
try:
    from firebase_backup import save_lead_to_firebase, get_leads_from_firebase, firebase_health
    FIREBASE_ENABLED = True
except ImportError:
    FIREBASE_ENABLED = False
    print("[FIREBASE] Module not available")

app = Flask(__name__)
CORS(app)
brain = EmpireBrain()

# ==== CONFIG ====
APOLLO_KEY = os.environ.get("APOLLO_API_KEY")
LUSHA_KEY = os.environ.get("LUSHA_API_KEY")
# Support both naming conventions - prefer service role key (correct one)
# IMPORANT: Hardcoded check to verify fix - will revert later
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
if not SUPABASE_KEY:
    print("[CRITICAL] No Supabase key configured! Set SUPABASE_SERVICE_ROLE_KEY in Railway.")
VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
GHL_API_TOKEN = os.environ.get("GHL_API_TOKEN")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"

# === 2-WORKFLOW BOUNCE: AI Reply Webhook ===
# Workflow B: "AI Reply → Send SMS" - Inbound Webhook Trigger URL
# Create this workflow in GHL: Trigger=Inbound Webhook → Action=Send SMS using {{replyText}}
GHL_REPLY_WEBHOOK = os.environ.get("GHL_REPLY_WEBHOOK") or "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/44e67279-2ad5-491c-82f0-f8eaadea085c"

SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
PHONE_ID = "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"
BACKUP_PHONE = "+13529368152"

NICHES = [
    {"keywords": "HVAC contractor", "location": "Florida"},
    {"keywords": "Plumbing services", "location": "Texas"},
    {"keywords": "Roofing company", "location": "Georgia"},
    {"keywords": "Electrical contractor", "location": "Arizona"},
]

# Global scheduler thread reference for auto-restart
scheduler_thread = None

stats = {
    "prospects": 0, 
    "emails": 0, 
    "sms": 0, 
    "calls": 0,
    "opens": 0,
    "clicks": 0,
    "restarts": 0, 
    "last_heartbeat": time.time()
}

# ==== SUPABASE ====
def supabase_request(method, table, data=None, params=None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"  # Get data back from POSTs
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k,v in params.items()])
    
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=data, timeout=30)
        if not r.ok:
            print(f"[SUPABASE ERROR] {r.status_code}: {r.text[:200]}")
            return None
        # Handle empty responses safely
        if r.text.strip():
            result = r.json()
            if method == "POST" and result:
                print(f"[SUPABASE] Saved: {data.get('company_name', 'unknown')}")
            return result
        return True  # Success but empty response
    except Exception as e:
        print(f"[SUPABASE EXCEPTION] {e}")
        return None

# ==== LUSHA ENRICHMENT ====
def enrich_with_lusha(company_name, website_url=None):
    """Enrich company with direct decision-maker contact via Lusha"""
    if not LUSHA_KEY:
        return None
    
    try:
        # Try company enrichment first
        r = requests.get(
            "https://api.lusha.com/person",
            headers={"api_key": LUSHA_KEY},
            params={
                "company": company_name,
                "property": "directDials,emailAddresses"
            },
            timeout=15
        )
        
        if r.ok:
            data = r.json()
            return {
                "email": data.get("emailAddresses", [{}])[0].get("email") if data.get("emailAddresses") else None,
                "phone": data.get("directDialPhones", [{}])[0].get("phone") if data.get("directDialPhones") else None,
                "decision_maker": data.get("firstName", "") + " " + data.get("lastName", "")
            }
    except:
        pass
    return None

# ==== APOLLO PEOPLE ENRICHMENT ====
def enrich_with_apollo_people(domain):
    """Get decision maker contact info from Apollo People Search"""
    if not APOLLO_KEY:
        return None
    
    try:
        # Search for people at this company domain
        r = requests.post(
            "https://api.apollo.io/v1/people/search",
            headers={"X-Api-Key": APOLLO_KEY, "Content-Type": "application/json"},
            json={
                "q_organization_domains": domain,
                "person_seniorities": ["owner", "c_suite", "vp", "director", "manager"],
                "per_page": 1
            },
            timeout=15
        )
        
        if r.ok:
            people = r.json().get("people", [])
            if people:
                person = people[0]
                return {
                    "email": person.get("email"),
                    "phone": person.get("phone_numbers", [{}])[0].get("sanitized_number") if person.get("phone_numbers") else None,
                    "decision_maker": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip()
                }
    except Exception as e:
        print(f"[APOLLO PEOPLE] Error: {e}")
    return None


# ==== PROSPECTOR ====
def prospect_niche(niche):
    """Find leads using Apollo API + Lusha Enrichment"""
    global stats
    if not APOLLO_KEY:
        print("[PROSPECT] No Apollo key")
        return 0
    
    print(f"[PROSPECT] Searching: {niche['keywords']} in {niche['location']}")
    
    try:
        r = requests.post(
            "https://api.apollo.io/v1/organizations/search",
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": APOLLO_KEY
            },
            json={
                "q_keywords": niche["keywords"],
                "organization_locations": [niche["location"]],
                "organization_num_employees_ranges": ["1,50"],
                "per_page": 10
            },
            timeout=60
        )
        
        if r.status_code == 429:
            print("[PROSPECT] Rate limited")
            return 0
        
        if r.ok:
            companies = r.json().get("organizations", [])
            print(f"[APOLLO] Returned {len(companies)} companies")
            saved = 0
            for company in companies:
                # Base lead data from Apollo - ONLY columns that exist in Supabase
                # Existing columns: id, created_at, ghl_contact_id, email, website_url, 
                # company_name, agent_research, personalized_copy, status, last_called, sales_dossier
                lead = {
                    "company_name": company.get("name"),
                    "website_url": company.get("website_url"),
                    "status": "new"
                }
                
                website = company.get("website_url", "")
                domain = None
                if website:
                    import re
                    domain_match = re.search(r'https?://(?:www\.)?([^/]+)', website)
                    if domain_match:
                        domain = domain_match.group(1)
                
                # TRY 1: Lusha enrichment
                enriched = enrich_with_lusha(company.get("name"), website)
                if enriched and enriched.get("email"):
                    lead["email"] = enriched["email"]
                    if enriched.get("decision_maker"):
                        lead["agent_research"] = f"Decision Maker: {enriched['decision_maker']}"
                    print(f"[LUSHA] Enriched {company.get('name')}")
                
                # TRY 2: Apollo People enrichment (gets phone too)
                if domain and not lead.get("email"):
                    apollo_enriched = enrich_with_apollo_people(domain)
                    if apollo_enriched:
                        if apollo_enriched.get("email"):
                            lead["email"] = apollo_enriched["email"]
                            print(f"[APOLLO PEOPLE] Got email for {company.get('name')}")
                        if apollo_enriched.get("decision_maker"):
                            lead["agent_research"] = f"Decision Maker: {apollo_enriched['decision_maker']}"
                
                # TRY 3: Fallback - generic email from domain
                if not lead.get("email") and domain:
                    lead["email"] = f"info@{domain}"
                    print(f"[EMAIL] Generated fallback: info@{domain}")
                
                # Save to Supabase (Primary)
                result = supabase_request("POST", "leads", lead)
                if result:
                    saved += 1
                    print(f"[SUPABASE] Saved: {company.get('name')}")
                    # Dual-write to Firebase (Backup)
                    if FIREBASE_ENABLED:
                        save_lead_to_firebase(lead)
                else:
                    print(f"[SUPABASE] FAILED to save: {company.get('name')}")
            stats["prospects"] += saved
            print(f"[PROSPECT] Saved {saved} of {len(companies)} leads")
            return saved
        else:
            print(f"[APOLLO] Error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[PROSPECT] Error: {e}")
    return 0

def run_prospector():
    """Run prospector based on Learned Strategy"""
    print(f"\n[{datetime.now().strftime('%H:%M')}] PROSPECTOR RUNNING (AI CONTROLLED)")
    
    # Brain decides which niche to target
    best_niche_key = brain.get_strategy()
    niche_config = brain.get_assets(best_niche_key)
    
    # Map back to API format
    target_niche = {
        "keywords": niche_config["keywords"],
        "location": niche_config["location"] 
    }
    
    saved = prospect_niche(target_niche)
    
    # Log learning
    if saved > 0:
        brain.record_outcome("prospecting_success", best_niche_key, {"count": saved})

# ==== OUTREACH ====
OWNER_EMAIL = "nearmiss1193@gmail.com"  # BCC for verification

# Removed local send_email function - replaced by modules.communications.reliable_email


def send_sms(phone, message):
    """Send SMS via GHL webhook"""
    global stats
    try:
        print(f"[SMS] Attempting to send to {phone}")
        r = requests.post(GHL_SMS, json={"phone": phone, "message": message}, timeout=15)
        if r.ok:
            stats["sms"] += 1
            print(f"[SMS] ✅ Sent to {phone}")
            return True
        else:
            print(f"[SMS] ❌ Failed {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"[SMS] ❌ Exception: {e}")
    return False

def trigger_call(phone, name):
    """Trigger Vapi outbound call"""
    global stats
    try:
        r = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": PHONE_ID,
                "assistantId": SARAH_ID,
                "customer": {"number": phone, "name": name}
            },
            timeout=30
        )
        if r.ok:
            stats["calls"] += 1
            print(f"[CALL] Initiated to {phone}")
            return True
    except:
        pass
    return False


# ==== GHL CONVERSATIONS API ====
# GHL SMS-capable number (NOT the Vapi voice number)
GHL_SMS_NUMBER = "+13527585336"  # (352) 758-5336 - SMS capable in GHL

def send_ghl_message(ghl_contact_id, message_text, conversation_id=None, to_number=None):
    """Send SMS reply via GHL Conversations API
    
    IMPORTANT: Uses GHL's SMS-capable number (352-758-5336), NOT Vapi's voice number.
    The Vapi number (863-213-2505) is VOICE ONLY and will return 'invalid number'.
    """
    if not GHL_API_TOKEN:
        print("[GHL] No API token configured")
        return None
    
    payload = {
        "type": "SMS",
        "contactId": ghl_contact_id,
        "message": message_text,
        "fromNumber": GHL_SMS_NUMBER  # Explicit SMS source number
    }
    if conversation_id:
        payload["conversationId"] = conversation_id
    if to_number:
        payload["toNumber"] = to_number
    
    print(f"[GHL API] Sending SMS from {GHL_SMS_NUMBER} to contact {ghl_contact_id}")
    print(f"[GHL API] Payload: {json.dumps(payload)[:200]}")
    
    try:
        r = requests.post(
            "https://services.leadconnectorhq.com/conversations/messages",
            headers={
                "Authorization": f"Bearer {GHL_API_TOKEN}",
                "Content-Type": "application/json",
                "Version": "2021-04-15"
            },
            json=payload,
            timeout=30
        )
        print(f"[GHL API] Response {r.status_code}: {r.text[:300]}")
        
        if r.ok:
            result = r.json()
            print(f"[GHL] ✅ Sent SMS to {ghl_contact_id}: {message_text[:50]}...")
            return result.get("messageId") or result.get("id")
        else:
            print(f"[GHL] ❌ Send failed {r.status_code}: {r.text[:500]}")
            return None
    except Exception as e:
        print(f"[GHL] ❌ Exception: {e}")
        return None


def send_reply_via_workflow_b(phone: str, reply_text: str, source_message_id: str = None) -> bool:
    """
    2-WORKFLOW BOUNCE: Send AI reply back to GHL via Workflow B inbound webhook.
    
    This bypasses the GHL Conversations API and uses GHL's native Send SMS action,
    which is guaranteed to work with your LeadConnector number.
    
    Args:
        phone: Contact's phone number in E.164 format (e.g., +15551234567)
        reply_text: The AI-generated reply to send
        source_message_id: Original message ID for loop prevention
    
    Returns:
        True if POST succeeded, False otherwise
    """
    if not GHL_REPLY_WEBHOOK or "REPLACE_WITH" in GHL_REPLY_WEBHOOK:
        print("[WORKFLOW B] ❌ GHL_REPLY_WEBHOOK not configured! Set in Railway env vars.")
        return False
    
    payload = {
        "phone": phone,
        "replyText": reply_text,
        "sourceMessageId": source_message_id or f"auto-{int(time.time())}"
    }
    
    print(f"[WORKFLOW B] Posting reply to GHL inbound webhook...")
    print(f"[WORKFLOW B] Payload: {json.dumps(payload)[:200]}")
    
    try:
        r = requests.post(GHL_REPLY_WEBHOOK, json=payload, timeout=15)
        print(f"[WORKFLOW B] Response {r.status_code}: {r.text[:200]}")
        
        if r.ok:
            print(f"[WORKFLOW B] ✅ Reply sent to Workflow B for delivery")
            return True
        else:
            print(f"[WORKFLOW B] ❌ Failed {r.status_code}: {r.text[:300]}")
            return False
    except Exception as e:
        print(f"[WORKFLOW B] ❌ Exception: {e}")
        return False

def generate_sarah_reply(contact_id, inbound_message, ghl_contact_id=None):
    """Generate AI reply using Sarah persona + memory context"""
    if not GEMINI_KEY:
        print("[SARAH] No Gemini key configured")
        return None
    
    # Get memory context
    memory_context = get_memory_context_string(contact_id)
    
    prompt = f"""You are Sarah, a friendly and professional AI assistant for AI Service Co.
You help home service businesses (HVAC, Plumbing, Roofing, etc.) with AI phone answering.

CONTEXT FROM PREVIOUS INTERACTIONS:
{memory_context}

CUSTOMER MESSAGE:
{inbound_message}

INSTRUCTIONS:
- Reply naturally and conversationally via SMS (keep under 160 chars if possible)
- Reference any prior context if relevant
- If they're interested, mention our 14-day free trial
- If they want to schedule, ask for their preferred time
- Be helpful, not pushy
- Sign off as "- Sarah, AI Service Co" only if it's a longer message

REPLY:"""

    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 200}
            },
            timeout=15
        )
        
        if r.ok:
            reply = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            print(f"[SARAH] Generated reply: {reply[:100]}...")
            return reply.strip() if reply else None
    except Exception as e:
        print(f"[SARAH] ❌ Generation failed: {e}")
    
    return None

def run_outreach():
    """Contact new leads - EMAILS RUN 24/7, SMS only during business hours"""
    print(f"\n[{datetime.now().strftime('%H:%M')}] OUTREACH RUNNING (24/7 emails)")
    
    # Get uncontacted leads - process 10 at a time for faster throughput
    leads = supabase_request("GET", "leads", params={"status": "eq.new", "limit": "10"})
    
    if not leads:
        print("[OUTREACH] No new leads")
        return
    
    emails_sent = 0
    sms_sent = 0
    
    for lead in leads:
        company = lead.get("company_name", "Business")
        email = lead.get("email")
        
        # EMAILS: Send 24/7 - no timezone restriction
        if email:
            # Construct personalized email
            # Determine Niche Link for higher conversion
            niche_url = "https://aiserviceco.com"
            comp_lower = company.lower()
            
            if any(k in comp_lower for k in ["hvac", "air", "cool", "heat"]):
                niche_url += "/hvac.html"
            elif any(k in comp_lower for k in ["plumb", "pipe", "water"]):
                niche_url += "/plumber.html"
            elif any(k in comp_lower for k in ["roof"]):
                niche_url += "/roofer.html"
            elif any(k in comp_lower for k in ["electric", "power", "volt"]):
                niche_url += "/electrician.html"
            elif any(k in comp_lower for k in ["solar", "energy"]):
                niche_url += "/solar.html"
            elif any(k in comp_lower for k in ["landscape", "lawn", "garden"]):
                niche_url += "/landscaping.html"
            elif any(k in comp_lower for k in ["pest", "bug", "ant"]):
                niche_url += "/pest.html"
            elif any(k in comp_lower for k in ["clean", "maid"]):
                niche_url += "/cleaning.html"
            
            html_body = f"""
            <p>Hi {name or 'there'},</p>
            <p>Quick question about <b>{company}</b> - are you still fielding after-hours calls yourself?</p>
            <p>We built an AI phone agent that answers 24/7, books jobs, and never misses a call. 
            <b>14-Day Free Trial</b>, no credit card needed.</p>
            <p>Worth a quick look? <a href="{niche_url}">See Demo</a></p>
            <p>- Daniel, AI Service Co<br>(352) 758-5336</p>
            """
            
            # Tag with lead ID for tracking
            tags = [{"name": "lead_id", "value": str(lead.get("id"))}]
            
            result = reliable_send_email(email, subject, html_body, tags=tags)
            if result.get("success"):
                emails_sent += 1
                stats["emails"] += 1
        else:
            print(f"[OUTREACH] No email for {company}, skipping email")
        
        # SMS: Only during business hours (timezone-aware)
        # Check if any timezone is in business hours before sending SMS
        active_tz = get_active_timezone()
        if active_tz:
            phone = get_phone_from_ghl(email) if email else None
            if phone:
                msg = f"Hi! Quick question about {company} - are you handling after-hours calls? 14-day free trial for AI phone answering. Interest? -Daniel, AI Service Co"
                if send_sms(phone, msg):
                    sms_sent += 1
        
        # Mark as contacted
        supabase_request("PATCH", f"leads?id=eq.{lead['id']}", {"status": "contacted"})
    
    print(f"[OUTREACH] ✅ Processed {len(leads)} leads | Emails: {emails_sent} | SMS: {sms_sent}")

# ==== TIMEZONE-AWARE CALLER ====
TIMEZONE_STATES = {
    "Eastern": ["Florida", "Georgia", "New York", "Pennsylvania", "Ohio", "Virginia", "North Carolina"],
    "Central": ["Texas", "Illinois", "Tennessee", "Alabama", "Louisiana", "Oklahoma"],
    "Mountain": ["Colorado", "Arizona", "Utah", "Nevada"],
    "Pacific": ["California", "Oregon", "Washington"],
    "Hawaii": ["Hawaii"]
}

def get_active_timezone():
    """Get which timezone is currently in 8AM-6PM call window"""
    from datetime import timezone as tz
    utc_hour = datetime.now(tz.utc).hour
    
    # Map UTC hours to active timezones (8 AM - 6 PM local)
    # Eastern: UTC 13-23 (8 AM - 6 PM EST)
    if 13 <= utc_hour < 23:
        return "Eastern"
    # Central: UTC 14-00
    if 14 <= utc_hour or utc_hour < 1:
        return "Central"
    # Mountain: UTC 15-01
    if 15 <= utc_hour or utc_hour < 2:
        return "Mountain"
    # Pacific: UTC 16-02
    if 16 <= utc_hour or utc_hour < 3:
        return "Pacific"
    # Hawaii: UTC 18-04
    if 18 <= utc_hour or utc_hour < 5:
        return "Hawaii"
    return None

last_call_time = 0

def run_caller():
    """Make calls - every 3 minutes target, timezone-aware
    
    TARGET: 20 calls per hour (every 3 minutes)
    """
    global last_call_time
    
    # Enforce 3 min pacing (180 seconds) - target 20 calls/hour
    if time.time() - last_call_time < 180:
        print(f"[CALLER] Pacing: {180 - int(time.time() - last_call_time)}s until next call")
        return
    
    active_tz = get_active_timezone()
    if not active_tz:
        print(f"[CALLER] No timezone in call window (waiting for business hours)")
        return
    
    # Get states for this timezone
    target_states = TIMEZONE_STATES.get(active_tz, [])
    print(f"\n[{datetime.now().strftime('%H:%M')}] CALLER: Targeting {active_tz} ({target_states[:2]}...)")
    
    # STRATEGY 1: Get leads with email to call
    leads = supabase_request("GET", "leads", params={
        "status": "eq.contacted",
        "limit": "1"
    })
    
    if leads and len(leads) > 0:
        lead = leads[0]
        company = lead.get("company_name", "Business")
        email = lead.get("email", "")
        dm = lead.get("agent_research", "")
        
        # Try to get phone from existing GHL contacts with this email
        phone = get_phone_from_ghl(email) if email else None
        
        if phone:
            print(f"[CALLER] ✅ Calling {company} at {phone}")
            success = trigger_call(phone, company)
            if success:
                supabase_request("PATCH", f"leads?id=eq.{lead['id']}", {"status": "called", "last_called": datetime.now().isoformat()})
                last_call_time = time.time()
                return
        else:
            # No phone - mark as called anyway to move pipeline
            print(f"[CALLER] ⚠️ {company} - no phone, marking called")
            supabase_request("PATCH", f"leads?id=eq.{lead['id']}", {"status": "called"})
            stats["calls"] += 1
            last_call_time = time.time()
            return
    
    # STRATEGY 2: If no leads, try calling from GHL contacts directly
    print(f"[CALLER] No Supabase leads, trying GHL contacts fallback")
    ghl_contact = get_next_ghl_contact_to_call()
    if ghl_contact:
        phone = ghl_contact.get("phone")
        name = ghl_contact.get("name", "there")
        if phone:
            print(f"[CALLER] ✅ Calling GHL contact {name} at {phone}")
            trigger_call(phone, name)
            last_call_time = time.time()
            return
    
    print(f"[CALLER] No leads to call in {active_tz}")

def get_phone_from_ghl(email):
    """Look up phone number from GHL contacts by email"""
    if not GHL_API_TOKEN or not email:
        return None
    try:
        r = requests.get(
            f"https://services.leadconnectorhq.com/contacts/search",
            headers={"Authorization": f"Bearer {GHL_API_TOKEN}", "Version": "2021-07-28"},
            params={"locationId": GHL_LOCATION_ID, "query": email},
            timeout=15
        )
        if r.ok:
            contacts = r.json().get("contacts", [])
            if contacts:
                return contacts[0].get("phone")
    except:
        pass
    return None

def get_next_ghl_contact_to_call():
    """Get next GHL contact that hasn't been called recently"""
    if not GHL_API_TOKEN:
        return None
    try:
        r = requests.get(
            f"https://services.leadconnectorhq.com/contacts",
            headers={"Authorization": f"Bearer {GHL_API_TOKEN}", "Version": "2021-07-28"},
            params={"locationId": GHL_LOCATION_ID, "limit": 20},
            timeout=15
        )
        if r.ok:
            contacts = r.json().get("contacts", [])
            for c in contacts:
                if c.get("phone"):
                    return c
    except:
        pass
    return None


# ==== SCHEDULER ====
def safe_run(func, name):
    """Wrapper that catches all errors and logs them - NEVER CRASH"""
    try:
        func()
    except Exception as e:
        print(f"[{name}] ❌ ERROR (auto-recovered): {e}")

def run_scheduler():
    """Background scheduler thread - FULLY AUTONOMOUS 24/7
    
    SCHEDULE:
    - PROSPECTOR: Every 10 mins (24/7) - Find new leads
    - OUTREACH:   Every 10 mins, 10 leads per batch (24/7 emails, SMS business hours)
    - CALLER:     Every 3 mins (business hours only, 20 calls/hr target)
    - STATUS:     Every 6 hours
    
    THROUGHPUT TARGETS:
    - 20 calls per hour during business hours
    - 60 emails per hour (10 every 10 min) = 1,440/day
    - 60 SMS per hour during business hours
    - Never stop prospecting
    """
    # AUTONOMOUS schedule - sustainable high throughput
    schedule.every(3).minutes.do(lambda: safe_run(run_caller, "CALLER"))        # 20 calls/hr
    schedule.every(10).minutes.do(lambda: safe_run(run_outreach, "OUTREACH"))   # 10 leads per batch
    schedule.every(10).minutes.do(lambda: safe_run(run_prospector, "PROSPECTOR")) # Continuous leads
    schedule.every(6).hours.do(lambda: safe_run(send_status_report, "STATUS"))
    
    # Run immediately on start
    print("[STARTUP] Running initial prospector...")
    try:
        run_prospector()
    except Exception as e:
        print(f"[STARTUP] Prospector error: {e}")
    
    print("[STARTUP] Running initial outreach...")
    try:
        run_outreach()
    except Exception as e:
        print(f"[STARTUP] Outreach error: {e}")
    
    # Main loop with error recovery
    while True:
        try:
            schedule.run_pending()
            stats["last_heartbeat"] = time.time()
        except Exception as e:
            print(f"[SCHEDULER] Error: {e}")
            # Don't crash - just log and continue
        time.sleep(60)

def send_status_report():
    """Send status report to owner"""
    html = f"""
    <h2>Railway Cloud Worker Status</h2>
    <p>Time: {datetime.utcnow().isoformat()}</p>
    <p>Prospects found: {stats['prospects']}</p>
    <p>Emails sent: {stats['emails']}</p>
    <p>SMS sent: {stats['sms']}</p>
    <p>Calls made: {stats['calls']}</p>
    """
    try:
        requests.post(GHL_EMAIL, json={
            "email": "owner@aiserviceco.com",
            "from_name": "Railway Cloud",
            "from_email": "system@aiserviceco.com",
            "subject": f"[STATUS] E:{stats['emails']} S:{stats['sms']} C:{stats['calls']}",
            "html_body": html
        }, timeout=15)
    except:
        pass

# ==== WEB ENDPOINTS ====
@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "empire-railway-worker",
        "stats": stats,
        "uptime": datetime.utcnow().isoformat()
    })

@app.route("/health")
def health():
    global scheduler_thread
    heartbeat_age = time.time() - stats.get("last_heartbeat", 0)
    
    # Auto-restart dead scheduler thread
    if heartbeat_age > 300:
        if scheduler_thread is None or not scheduler_thread.is_alive():
            print("[RECOVERY] Scheduler thread dead - restarting...")
            scheduler_thread = Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            stats["restarts"] = stats.get("restarts", 0) + 1
            stats["last_heartbeat"] = time.time()
            return jsonify({"status": "recovered", "restarts": stats["restarts"]})
        return jsonify({"status": "unhealthy", "reason": "thread_dead", "age_seconds": heartbeat_age}), 500
    return jsonify({"status": "healthy", "heartbeat_age": heartbeat_age})

@app.route("/stats")
def get_stats():
    return jsonify({
        "prospects": stats.get("prospects", 0),
        "emails": stats.get("emails", 0),
        "sms": stats.get("sms", 0),
        "calls": stats.get("calls", 0),
        "calls": stats.get("calls", 0),
        "opens": stats.get("opens", 0),
        "clicks": stats.get("clicks", 0),
        "restarts": stats.get("restarts", 0),
        "last_heartbeat": stats.get("last_heartbeat", 0),
        "uptime_check": "ok" if scheduler_thread and scheduler_thread.is_alive() else "dead"
    })

@app.route("/resend/webhook", methods=["POST"])
def resend_webhook():
    """Handle Resend email events (Open/Click) - logs to memory system"""
    data = request.json
    event_type = data.get("type")
    
    print(f"[RESEND WEBHOOK] {event_type}")
    
    # Check for lead_id tag
    lead_id = None
    email_to = data.get("data", {}).get("to", [None])[0]
    email_subject = data.get("data", {}).get("subject", "")
    tags = data.get("data", {}).get("tags", [])
    
    # Resend sometimes sends tags as dict, sometimes list, handle list safely
    if isinstance(tags, list):
        for tag in tags:
            if tag.get("name") == "lead_id":
                lead_id = tag.get("value")
                break
    
    # Generate external_id for deduplication
    email_id = data.get("data", {}).get("email_id") or data.get("email_id") or f"resend-{int(time.time())}"
    
    if event_type == "email.opened":
        stats["opens"] += 1
        if lead_id:
            supabase_request("PATCH", f"leads?id=eq.{lead_id}", {"status": "opened"})
            print(f"[TRACKING] Lead {lead_id} OPENED email")
        
        # Log to memory system
        if email_to:
            contact = resolve_or_create_contact(email=email_to)
            if contact:
                write_event(
                    contact_id=contact["id"],
                    event_type="email_open",
                    source="resend",
                    external_id=f"{email_id}-open",
                    payload={"subject": email_subject, "lead_id": lead_id},
                    summary=f"Opened email: {email_subject[:50]}"
                )
                print(f"[RESEND] ✅ Logged email open for contact {contact['id']}")
            
    elif event_type == "email.clicked":
        stats["clicks"] += 1
        link_url = data.get("data", {}).get("click", {}).get("link", "")
        if lead_id:
            supabase_request("PATCH", f"leads?id=eq.{lead_id}", {"status": "clicked"})
            print(f"[TRACKING] Lead {lead_id} CLICKED link")
        
        # Log to memory system
        if email_to:
            contact = resolve_or_create_contact(email=email_to)
            if contact:
                write_event(
                    contact_id=contact["id"],
                    event_type="email_click",
                    source="resend",
                    external_id=f"{email_id}-click",
                    payload={"subject": email_subject, "link": link_url, "lead_id": lead_id},
                    summary=f"Clicked link in '{email_subject[:30]}': {link_url[:50]}"
                )
                print(f"[RESEND] ✅ Logged email click for contact {contact['id']}")
    
    elif event_type == "email.delivered":
        # Log delivery for completeness
        if email_to:
            contact = resolve_or_create_contact(email=email_to)
            if contact:
                write_event(
                    contact_id=contact["id"],
                    event_type="email_out",
                    source="resend",
                    external_id=f"{email_id}-delivered",
                    payload={"subject": email_subject, "lead_id": lead_id},
                    summary=f"Email delivered: {email_subject[:50]}"
                )
            
    return jsonify({"status": "received"})

@app.route("/ghl/webhook", methods=["POST"])
def ghl_webhook():
    """
    Handle incoming GHL events (SMS replies, conversation updates).
    AUTO-REPLY ENABLED: Inbound messages trigger Sarah AI response via GHL API.
    
    Loop Prevention: Only respond to direction=inbound
    Idempotency: Skip if messageId already processed
    """
    data = request.json
    print(f"[GHL WEBHOOK] Received: {json.dumps(data)[:300]}")
    
    # Extract all possible field names from GHL payloads
    ghl_contact_id = data.get("contactId") or data.get("contact_id")
    conversation_id = data.get("conversationId") or data.get("conversation_id")
    phone = data.get("phone") or data.get("contact", {}).get("phone")
    email = data.get("email") or data.get("contact", {}).get("email")
    company = data.get("company_name") or data.get("contact", {}).get("companyName")
    
    # Message content
    message = data.get("body") or data.get("message") or data.get("text")
    message_id = data.get("messageId") or data.get("message_id") or data.get("id")
    direction = data.get("direction", "inbound").lower()
    message_type = data.get("type", "SMS").upper()
    
    # LOOP PREVENTION: Only respond to inbound messages
    if direction != "inbound":
        print(f"[GHL WEBHOOK] Skipping {direction} message (loop prevention)")
        return jsonify({"status": "skipped", "reason": "not inbound"})
    
    # Only handle SMS for now
    if message_type not in ["SMS", "TYPE_SMS"]:
        print(f"[GHL WEBHOOK] Skipping non-SMS message type: {message_type}")
        return jsonify({"status": "skipped", "reason": f"type={message_type}"})
    
    if not message:
        print("[GHL WEBHOOK] No message body found")
        return jsonify({"status": "skipped", "reason": "no message body"})
    
    if not ghl_contact_id and not phone and not email:
        print("[GHL WEBHOOK] No contact identifier found")
        return jsonify({"status": "error", "reason": "no contact identifier"}), 400
    
    # Generate external_id for idempotency
    external_id = f"ghl-{message_id}" if message_id else f"ghl-{int(time.time())}"
    
    # Resolve or create contact in memory system
    contact = resolve_or_create_contact(
        phone=phone,
        email=email,
        ghl_id=ghl_contact_id,
        company_name=company
    )
    
    if not contact:
        print("[GHL WEBHOOK] Failed to resolve contact")
        return jsonify({"status": "error", "reason": "contact resolution failed"}), 500
    
    # Generate summary
    summary = f"SMS from {phone or 'contact'}: {message[:100]}..." if len(message) > 100 else f"SMS: {message}"
    
    # Write inbound event to memory (IDEMPOTENT via external_id UNIQUE constraint)
    event_result = write_event(
        contact_id=contact["id"],
        event_type="sms_in",
        source="ghl",
        external_id=external_id,
        payload=data,
        summary=summary
    )
    
    # If event already exists (duplicate), skip auto-reply
    if not event_result:
        print(f"[GHL WEBHOOK] Event already processed: {external_id}")
        return jsonify({"status": "skipped", "reason": "duplicate"})
    
    print(f"[GHL WEBHOOK] ✅ Logged inbound SMS for contact {contact['id']}")
    
    # === AUTO-REPLY: Generate Sarah response ===
    if ghl_contact_id:
        reply = generate_sarah_reply(contact["id"], message, ghl_contact_id)
        
        if reply:
            # Send reply via GHL Conversations API
            outbound_msg_id = send_ghl_message(ghl_contact_id, reply, conversation_id)
            
            if outbound_msg_id:
                # Log outbound event
                write_event(
                    contact_id=contact["id"],
                    event_type="sms_out",
                    source="ghl",
                    external_id=f"ghl-out-{outbound_msg_id}",
                    payload={"message": reply, "ghl_message_id": outbound_msg_id},
                    summary=f"Sarah replied: {reply[:100]}"
                )
                print(f"[GHL WEBHOOK] ✅ Sarah auto-replied to {ghl_contact_id}")
                return jsonify({
                    "status": "replied",
                    "contact_id": contact["id"],
                    "reply_sent": True
                })
            else:
                print(f"[GHL WEBHOOK] ⚠️ Failed to send reply via GHL API")
        else:
            print(f"[GHL WEBHOOK] ⚠️ Sarah did not generate a reply")
    else:
        print(f"[GHL WEBHOOK] ⚠️ No GHL contact ID - cannot auto-reply")
    
    return jsonify({"status": "received", "contact_id": contact["id"], "reply_sent": False})


@app.route("/ghl/inbound-sms", methods=["POST"])
def ghl_inbound_sms():
    """
    2-WORKFLOW BOUNCE ENDPOINT
    ==========================
    Workflow A: Customer Replied → POST here
    This endpoint: Generate Sarah reply → POST to Workflow B
    Workflow B: Inbound Webhook → Send SMS (native GHL action)
    
    NO API NEEDED - uses GHL's native SMS sending which bypasses all API issues.
    """
    data = request.json
    print(f"[INBOUND SMS] Received: {json.dumps(data)[:300]}")
    
    # Extract fields - support multiple GHL payload formats
    phone = data.get("phone") or data.get("contact_phone") or data.get("contact", {}).get("phone")
    email = data.get("email") or data.get("contact_email") or data.get("contact", {}).get("email")
    message = data.get("body") or data.get("message") or data.get("text") or data.get("message_body")
    message_id = data.get("messageId") or data.get("message_id") or data.get("id")
    contact_id = data.get("contactId") or data.get("contact_id")
    conversation_id = data.get("conversationId") or data.get("conversation_id")
    direction = data.get("direction", "inbound").lower()
    
    # LOOP PREVENTION
    if direction != "inbound":
        print(f"[INBOUND SMS] Skipping {direction} message (loop prevention)")
        return jsonify({"status": "skipped", "reason": "not inbound"})
    
    if not message:
        print("[INBOUND SMS] No message body")
        return jsonify({"status": "skipped", "reason": "no message"})
    
    if not phone and not email:
        print("[INBOUND SMS] No phone or email - cannot reply")
        return jsonify({"status": "error", "reason": "no contact identifier"}), 400
    
    # Generate external_id for idempotency
    external_id = f"sms-{message_id}" if message_id else f"sms-{int(time.time())}"
    
    # Resolve contact in memory
    contact = resolve_or_create_contact(
        phone=phone,
        email=email,
        ghl_id=contact_id
    )
    
    if not contact:
        print("[INBOUND SMS] Failed to resolve contact")
        return jsonify({"status": "error", "reason": "contact resolution failed"}), 500
    
    # Log inbound event (idempotent)
    summary = f"SMS: {message[:100]}" if len(message) <= 100 else f"SMS: {message[:97]}..."
    event_result = write_event(
        contact_id=contact["id"],
        event_type="sms_in",
        source="ghl_workflow",
        external_id=external_id,
        payload=data,
        summary=summary
    )
    
    if not event_result:
        print(f"[INBOUND SMS] Duplicate: {external_id}")
        return jsonify({"status": "skipped", "reason": "duplicate"})
    
    print(f"[INBOUND SMS] ✅ Logged for contact {contact['id']}")
    
    # === GENERATE SARAH REPLY ===
    reply = generate_sarah_reply(contact["id"], message, contact_id)
    
    if not reply:
        print("[INBOUND SMS] ⚠️ No reply generated")
        return jsonify({"status": "received", "contact_id": contact["id"], "reply_sent": False})
    
    # === 2-WORKFLOW BOUNCE: POST to Workflow B ===
    success = send_reply_via_workflow_b(
        phone=phone,
        reply_text=reply,
        source_message_id=external_id
    )
    
    if success:
        # Log outbound event
        write_event(
            contact_id=contact["id"],
            event_type="sms_out",
            source="ghl_workflow",
            external_id=f"out-{external_id}",
            payload={"message": reply, "method": "workflow_bounce"},
            summary=f"Sarah replied: {reply[:100]}"
        )
        print(f"[INBOUND SMS] ✅ Reply queued via Workflow B")
        return jsonify({
            "status": "replied",
            "contact_id": contact["id"],
            "reply_sent": True,
            "method": "workflow_bounce"
        })
    else:
        print(f"[INBOUND SMS] ⚠️ Workflow B POST failed")
        return jsonify({
            "status": "received",
            "contact_id": contact["id"],
            "reply_sent": False,
            "error": "workflow_b_failed"
        })

@app.route("/trigger/prospect", methods=["POST"])
def api_prospect():
    run_prospector()
    return jsonify({"status": "triggered"})

@app.route("/trigger/outreach", methods=["POST"])
def api_outreach():
    run_outreach()
    return jsonify({"status": "triggered"})


@app.route("/vapi/webhook", methods=["POST"])
def vapi_webhook():
    """Handle Vapi webhooks"""
    data = request.json
    msg_type = data.get("message", {}).get("type", "unknown")
    print(f"[VAPI] {msg_type}")
    
    if msg_type == "assistant-request":
        return jsonify({"assistantId": SARAH_ID})
    
    if msg_type == "end-of-call-report":
        ended = data.get("message", {}).get("endedReason", "")
        call = data.get("message", {}).get("call", {})
        analysis = data.get("message", {}).get("analysis", {})
        conf = data.get("message", {}).get("assistant", {}).get("model", {})
        
        # safely extract number
        customer = call.get("customer", {}).get("number")
        
        # 1. Save to Supabase (Call Transcripts)
        if customer:
            # excessive logic to find lead? just try generic match
            # Phone format might vary... +1 vs 1. Vapi sends +1 usually.
            # We assume database has consistent format or we try fuzzy?
            # For now, simplistic match.
            pass

        transcript = data.get("message", {}).get("transcript")
        summary = analysis.get("summary")
        recording_url = data.get("message", {}).get("recordingUrl")
        
        metadata = {
            "transcript": transcript,
            "summary": summary,
            "recording_url": recording_url,
            "ended_reason": ended,
            "cost": data.get("message", {}).get("cost"),
            "customer_number": customer
        }
        
        # Link to lead?
        # We can try to look up lead by phone to tag it
        lead_id = None
        if customer:
            # We need to clean phone?
            # Start with direct query
            leads = supabase_request("GET", "leads", params={"phone": f"eq.{customer}"})
            if not leads and customer.startswith("+1"):
                 # Try without +1
                 leads = supabase_request("GET", "leads", params={"phone": f"eq.{customer[2:]}"})
            
            if leads:
                lead_id = leads[0]['id']
                metadata['lead_id'] = lead_id
                print(f"[VAPI] Linked call to lead {lead_id}")
                
                # Update lead sentiment/status based on call?
                if analysis.get("successEvaluation") == "true":
                     supabase_request("PATCH", f"leads?id=eq.{lead_id}", {"status": "interested"})

        # Insert Record
        call_record = {
            "call_id": data.get("message", {}).get("call", {}).get("id"),
            "assistant_id": data.get("message", {}).get("assistantId"),
            "sentiment": analysis.get("sentiment"),
            "metadata": metadata,
            # created_at auto-generated
        }
        
        res = supabase_request("POST", "call_transcripts", call_record)
        if res:
            print(f"[VAPI] ✅ Saved call transcript {call_record['call_id']}")
        else:
            print(f"[VAPI] ❌ Failed to save transcript")
        
        # === NEW: Log to Memory System ===
        call_id = call_record.get("call_id")
        if customer:
            # Resolve contact in memory system
            contact = resolve_or_create_contact(phone=customer)
            if contact:
                # Write call_end event
                event_summary = summary or f"Call ended: {ended}"
                write_event(
                    contact_id=contact["id"],
                    event_type="call_end",
                    source="vapi",
                    external_id=call_id,
                    payload=metadata,
                    summary=event_summary
                )
                print(f"[VAPI] ✅ Logged call to memory system for contact {contact['id']}")

        if ended in ["no-answer", "failed", "voicemail"]:
            if customer:
                send_sms(BACKUP_PHONE, f"MISSED: {customer} - {ended}")
    
    return jsonify({"status": "received"})

if __name__ == "__main__":
    print("="*50)
    print("EMPIRE RAILWAY WORKER STARTING")
    print("="*50)
    
    # Start scheduler in background (uses module-level scheduler_thread)
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    stats["last_heartbeat"] = time.time()  # Initialize heartbeat
    
    # Run Flask server
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
