"""
MODAL CLOUD CAMPAIGN v2 - Multi-Touch + Enrichment
Runs 24/7 on Modal with full 3-touch nurture sequence
"""
import modal
import json
from datetime import datetime, timedelta

app = modal.App("empire-campaign-v2")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests")

# Config
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
RESEND_API_KEY = "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"
BOOKING_LINK = "https://link.aiserviceco.com/discovery"


# ============================================================================
# TOUCH 1: Immediate outreach
# ============================================================================
@app.function(image=image, schedule=modal.Period(minutes=10), timeout=600)
def run_touch_1():
    """Touch 1: Immediate outreach to new leads"""
    import requests
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    print("=" * 60)
    print(f"TOUCH 1 - IMMEDIATE - {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    # Get new leads with contact info
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=headers,
        params={"status": "eq.new", "limit": 5}
    )
    leads = [l for l in (r.json() if r.status_code == 200 else []) if l.get("email") or l.get("phone")]
    
    print(f"Found {len(leads)} leads for Touch 1")
    
    sent = 0
    for lead in leads:
        company = lead.get("company_name", "Business")
        slug = company.lower().replace(" ", "-").replace("&", "and")[:30]
        audit_link = f"https://www.aiserviceco.com/audits/{slug}.html"
        
        # Send Email
        if lead.get("email"):
            r = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                json={
                    "from": "Sarah <sarah@aiserviceco.com>",
                    "to": [lead["email"]],
                    "subject": f"[PRIVATE] Marketing Audit for {company}",
                    "html": f"<p>Hi,</p><p>Your private marketing audit is ready: <a href='{audit_link}'>{audit_link}</a></p><p>Reply or call (863) 337-3705</p><p>-Sarah</p>"
                },
                timeout=15
            )
            if r.status_code == 200:
                print(f"  [EMAIL] {company}")
        
        # Send SMS
        if lead.get("phone"):
            r = requests.post(
                GHL_SMS_WEBHOOK,
                json={"phone": lead["phone"], "message": f"Hi! Your marketing audit for {company} is ready: {audit_link} - Reply for a free consultation. -Sarah"},
                timeout=15
            )
            if r.status_code == 200:
                print(f"  [SMS] {company}")
        
        # Update lead
        next_touch = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}",
            headers=headers,
            json={"status": "contacted", "last_touch": 1, "touch_1_at": datetime.utcnow().isoformat() + "Z", "next_touch_at": next_touch}
        )
        sent += 1
    
    return {"touch": 1, "sent": sent}


# ============================================================================
# TOUCH 2: +24h follow-up SMS
# ============================================================================
@app.function(image=image, schedule=modal.Period(minutes=30), timeout=300)
def run_touch_2():
    """Touch 2: +24h SMS follow-up"""
    import requests
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    now = datetime.utcnow().isoformat() + "Z"
    
    print("=" * 60)
    print(f"TOUCH 2 - +24H - {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=headers,
        params={"last_touch": "eq.1", "next_touch_at": f"lte.{now}", "limit": 10}
    )
    leads = [l for l in (r.json() if r.status_code == 200 else []) if l.get("phone")]
    
    print(f"Found {len(leads)} leads for Touch 2")
    
    sent = 0
    for lead in leads:
        company = lead.get("company_name", "Business")
        
        r = requests.post(
            GHL_SMS_WEBHOOK,
            json={"phone": lead["phone"], "message": f"Quick follow-up - did you get a chance to review your {company} audit? I can walk you through the key findings in 15 min: {BOOKING_LINK} -Sarah"},
            timeout=15
        )
        
        if r.status_code == 200:
            print(f"  [SMS] {company}")
            sent += 1
        
        next_touch = (datetime.utcnow() + timedelta(hours=48)).isoformat() + "Z"
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}",
            headers=headers,
            json={"last_touch": 2, "touch_2_at": datetime.utcnow().isoformat() + "Z", "next_touch_at": next_touch}
        )
    
    return {"touch": 2, "sent": sent}


# ============================================================================
# TOUCH 3: +72h final push (SMS + Email)
# ============================================================================
@app.function(image=image, schedule=modal.Period(hours=1), timeout=300)
def run_touch_3():
    """Touch 3: +72h final push SMS + Email"""
    import requests
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    now = datetime.utcnow().isoformat() + "Z"
    
    print("=" * 60)
    print(f"TOUCH 3 - +72H - {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=headers,
        params={"last_touch": "eq.2", "next_touch_at": f"lte.{now}", "limit": 10}
    )
    leads = r.json() if r.status_code == 200 else []
    
    print(f"Found {len(leads)} leads for Touch 3")
    
    sent = 0
    for lead in leads:
        company = lead.get("company_name", "Business")
        
        # SMS
        if lead.get("phone"):
            requests.post(
                GHL_SMS_WEBHOOK,
                json={"phone": lead["phone"], "message": f"Last chance - your {company} audit expires soon. Book a free 15-min call: {BOOKING_LINK} -Sarah"},
                timeout=15
            )
            sent += 1
        
        # Email
        if lead.get("email"):
            requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                json={
                    "from": "Sarah <sarah@aiserviceco.com>",
                    "to": [lead["email"]],
                    "subject": f"Final reminder: Your {company} audit",
                    "html": f"<p>Hi,</p><p>Last chance - your audit expires soon.</p><p><b><a href='{BOOKING_LINK}'>Book your free 15-minute call →</a></b></p><p>-Sarah</p>"
                },
                timeout=15
            )
        
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}",
            headers=headers,
            json={"last_touch": 3, "touch_3_at": datetime.utcnow().isoformat() + "Z", "status": "nurture_complete"}
        )
    
    return {"touch": 3, "sent": sent}


# ============================================================================
# ENRICHMENT: Run before Touch 1
# ============================================================================
@app.function(image=image, schedule=modal.Period(hours=2), timeout=600)
def run_enrichment():
    """Enrich leads missing email/phone before outreach"""
    import requests
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    print("=" * 60)
    print(f"LEAD ENRICHMENT - {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    # Get leads missing email
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=headers,
        params={"status": "eq.new", "email": "is.null", "enriched_at": "is.null", "limit": 5}
    )
    leads = r.json() if r.status_code == 200 else []
    
    print(f"Found {len(leads)} leads needing enrichment")
    
    enriched = 0
    for lead in leads:
        company = lead.get("company_name", "")
        city = lead.get("city", "")
        industry = lead.get("industry", "")
        
        # Use AI to find contact
        prompt = f"Find decision maker email for: {company}, {city}, {industry}. Return ONLY JSON: {{\"email\": \"email@co.com or null\", \"phone\": \"+1xxx or null\"}}"
        
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            
            if r.status_code == 200:
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                if "```" in text:
                    text = text.split("```")[1].split("```")[0].replace("json", "")
                contact = json.loads(text.strip())
                
                updates = {"enriched_at": datetime.utcnow().isoformat() + "Z"}
                if contact.get("email") and "@" in str(contact["email"]):
                    updates["email"] = contact["email"]
                if contact.get("phone"):
                    updates["phone"] = contact["phone"]
                
                if "email" in updates or "phone" in updates:
                    requests.patch(f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}", headers=headers, json=updates)
                    print(f"  ✅ {company}: {updates.get('email', 'no email')}")
                    enriched += 1
                else:
                    requests.patch(f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}", headers=headers, json={"enriched_at": datetime.utcnow().isoformat() + "Z"})
        except Exception as e:
            print(f"  ❌ {company}: {e}")
    
    return {"enriched": enriched}


@app.local_entrypoint()
def main():
    print("Deploying Empire Campaign v2...")
    print("Touch 1: Every 10 min")
    print("Touch 2: Every 30 min")
    print("Touch 3: Every 1 hour")
    print("Enrichment: Every 2 hours")
