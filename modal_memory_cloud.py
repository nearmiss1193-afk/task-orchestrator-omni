"""
Modal Cloud - Sarah Memory + Campaign (Self-Contained)
Runs 24/7 - no local files needed
"""
import modal

app = modal.App("sarah-memory-cloud")

image = modal.Image.debian_slim(python_version="3.11").pip_install("requests")

# All config inline
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/e7OGCxJpH6q7AXQPcRgR/webhook-trigger/c30d2de3-90c7-4401-bf44-5f41e9122d9f"
RESEND_API_KEY = "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy"


@app.function(image=image, schedule=modal.Period(minutes=10), timeout=600)
def run_campaign():
    """Run outreach campaign every 10 minutes"""
    import requests
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    print("=" * 60)
    print("CLOUD CAMPAIGN - RUNNING")
    print("=" * 60)
    
    # Get new leads
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=headers,
        params={"status": "eq.new", "limit": 5}
    )
    
    leads = r.json() if r.status_code == 200 else []
    print(f"Found {len(leads)} leads to process")
    
    emails_sent = 0
    sms_sent = 0
    
    for lead in leads:
        company = lead.get("company_name", "Business")
        phone = lead.get("phone")
        email = lead.get("email")
        
        print(f"\nProcessing: {company}")
        
        slug = company.lower().replace(" ", "-").replace("&", "and")[:30]
        audit_link = f"https://www.aiserviceco.com/audits/{slug}.html"
        
        # Send email
        if email:
            try:
                resp = requests.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "from": "Sarah <sarah@aiserviceco.com>",
                        "to": [email],
                        "subject": f"[PRIVATE] Marketing Audit for {company}",
                        "html": f"<p>Hi,</p><p>Your private marketing audit is ready: <a href='{audit_link}'>{audit_link}</a></p><p>Reply or call (863) 337-3705</p><p>-Sarah</p>"
                    },
                    timeout=15
                )
                if resp.status_code == 200:
                    emails_sent += 1
                    print(f"  [EMAIL] Sent to {email}")
            except Exception as e:
                print(f"  [EMAIL FAIL] {e}")
        
        # Send SMS
        if phone:
            try:
                msg = f"Hi! Your marketing audit for {company} is ready: {audit_link} - Reply for a free consultation. -Sarah"
                resp = requests.post(
                    GHL_SMS_WEBHOOK,
                    json={"phone": phone, "message": msg},
                    timeout=15
                )
                if resp.status_code == 200:
                    sms_sent += 1
                    print(f"  [SMS] Sent to {phone}")
            except Exception as e:
                print(f"  [SMS FAIL] {e}")
        
        # Update lead status
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}",
            headers={**headers, "Content-Type": "application/json"},
            json={"status": "contacted"}
        )
    
    print(f"\n[STATS] Emails: {emails_sent}, SMS: {sms_sent}")
    return {"emails": emails_sent, "sms": sms_sent}


@app.function(image=image, schedule=modal.Period(hours=6), timeout=300)
def run_self_improvement():
    """Analyze interactions and suggest improvements every 6 hours"""
    import requests
    import json
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    print("=" * 60)
    print("SELF-IMPROVEMENT ANALYSIS")
    print("=" * 60)
    
    # Get recent interactions
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/interactions",
        headers=headers,
        params={"order": "created_at.desc", "limit": 50}
    )
    
    if r.status_code != 200:
        print("No interactions to analyze")
        return {}
    
    interactions = r.json()
    print(f"Analyzing {len(interactions)} interactions")
    
    # Prepare batch for AI analysis
    batch = json.dumps([
        {"outcome": i.get("outcome"), "intent": i.get("intent"), "sentiment": i.get("sentiment")}
        for i in interactions
    ])
    
    # Call Gemini for insights
    prompt = f"""Analyze these {len(interactions)} sales interactions and suggest improvements:
{batch}

Return JSON with:
- insights: top 3 observations
- suggested_changes: script improvements
"""
    
    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60
        )
        if resp.status_code == 200:
            result = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            print(result[:500])
            return {"analysis": result}
    except Exception as e:
        print(f"Analysis error: {e}")
    
    return {}


if __name__ == "__main__":
    print("Deploy with: modal deploy modal_memory_cloud.py")
