"""
Turbo Manus 24/7 Campaign - Modal Deployment
Uses Supabase REST API (not psycopg2) to avoid IPv6 connection issues
Runs every 10 minutes to process leads and send outreach
"""
import modal

# Minimal image with required dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("requests")
)

app = modal.App("turbo-manus-24-7")

# Supabase REST API Config
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/cf2e8a9c-e943-4d78-9f6f-cd66bb9a2e42"

@app.function(image=image, schedule=modal.Period(minutes=10), timeout=540)
def run_manus_cycle():
    """Execute one cycle of the turbo manus campaign using Supabase REST API"""
    import requests
    import time
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    print("=" * 50)
    print("TURBO MANUS CYCLE - MODAL CLOUD")
    print("=" * 50)
    
    try:
        # Get pending leads via REST API
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/leads",
            headers=headers,
            params={
                "status": "eq.pending",
                "or": "(email.not.is.null,phone.not.is.null)",
                "limit": 5
            },
            timeout=30
        )
        
        if resp.status_code != 200:
            print(f"[ERROR] DB fetch failed: {resp.status_code} {resp.text}")
            return {"error": resp.text}
        
        leads = resp.json()
        print(f"Found {len(leads)} pending leads")
        
        results = {"emails": 0, "sms": 0}
        
        for lead in leads:
            lead_id = lead.get("id")
            company = lead.get("company_name", "Business")
            email = lead.get("email")
            phone = lead.get("phone")
            
            print(f"\n[TARGET] {company}")
            
            # Generate audit link
            audit_link = f"https://aiserviceco.com/audits/{company.lower().replace(' ', '-').replace('.', '')}"
            
            # Send Email
            if email:
                try:
                    subject = f"ALERT - {company}: Revenue Opportunity Found"
                    body = f"""Hi,

I ran a free website and phone audit for {company}.

Your Custom Report: {audit_link}

Key Finding: Our analysis shows you're potentially leaving $144,000/year on the table.

Reply to this email or call (863) 337-3705.

Best,
Sarah
AI Service Co"""
                    
                    email_resp = requests.post(GHL_EMAIL_WEBHOOK, json={
                        "email": email,
                        "subject": subject,
                        "body": body
                    }, timeout=15)
                    if email_resp.status_code in [200, 201]:
                        results["emails"] += 1
                        print(f"   [OK] Email sent to {email}")
                    else:
                        print(f"   [FAIL] Email: {email_resp.status_code}")
                except Exception as e:
                    print(f"   [FAIL] Email: {e}")
            
            # Send SMS
            if phone:
                try:
                    msg = f"Hi! Just finished an audit for {company}. Found opportunities: {audit_link} - Reply for free consultation. -Sarah"
                    sms_resp = requests.post(GHL_SMS_WEBHOOK, json={
                        "phone": phone,
                        "message": msg
                    }, timeout=15)
                    if sms_resp.status_code in [200, 201]:
                        results["sms"] += 1
                        print(f"   [OK] SMS sent to {phone}")
                    else:
                        print(f"   [FAIL] SMS: {sms_resp.status_code}")
                except Exception as e:
                    print(f"   [FAIL] SMS: {e}")
            
            # Update status via REST API
            try:
                update_resp = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/leads",
                    headers=headers,
                    params={"id": f"eq.{lead_id}"},
                    json={"status": "contacted"},
                    timeout=15
                )
                if update_resp.status_code in [200, 204]:
                    print(f"   [OK] Status updated")
                else:
                    print(f"   [FAIL] DB update: {update_resp.status_code}")
            except Exception as e:
                print(f"   [FAIL] DB update: {e}")
            
            time.sleep(2)  # Rate limit
        
        print(f"\n[STATS] Cycle Complete: {results['emails']} emails, {results['sms']} SMS")
        return results
        
    except Exception as e:
        print(f"[ERROR] Cycle failed: {e}")
        raise e

@app.local_entrypoint()
def main():
    run_manus_cycle.remote()
