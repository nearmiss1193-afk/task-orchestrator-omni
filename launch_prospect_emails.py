# launch_prospect_emails.py - Send cold emails with John's link
import requests
import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Config
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
RESEND_KEY = os.getenv("RESEND_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

LANDING_PAGE = "https://client-portal-one-phi.vercel.app/roofing"

def send_email(to_email, company, first_name="there"):
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_KEY}",
        "Content-Type": "application/json"
    }
    
    # "John" persona email
    html_content = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <p>Hey {first_name},</p>
        <p>John here. Just tried calling {company} but missed you.</p>
        <p>Run a crew myself. We built an AI that handles estimates while you're on the roof. 
        It's answering calls for roofers in Florida right now.</p>
        <p>Want to hear it? I put a demo on this page (bottom right corner):</p>
        <p><a href="{LANDING_PAGE}" style="background-color: #ea580c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Test John AI Here</a></p>
        <p>It books inspections directly to your calendar. Pretty wild.</p>
        <p>Best,<br>John<br>AI Service Co</p>
    </div>
    """
    
    payload = {
        "from": "John <onboarding@resend.dev>", # Using dev domain for now
        "to": [to_email],
        "subject": f"Missed you at {company} (Roofing Tech)",
        "html": html_content
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        return res.status_code in [200, 201], res.json()
    except Exception as e:
        return False, str(e)

print("="*50)
print("LAUNCHING EMAIL CAMPAIGN: ROOFING")
print("="*50)

# Get harvested leads
leads = supabase.table('leads').select('*').eq('status', 'ready_to_send').execute()

roofing = []
for l in leads.data:
    ar = l.get('agent_research')
    if ar and isinstance(ar, dict) and ar.get('industry') == 'Roofing':
        roofing.append(l)

print(f"Found {len(roofing)} leads to email.")

for lead in roofing:
    email = lead.get('email')
    company = lead.get('company_name')
    
    if not email or 'test' in email:
        print(f"[SKIP] Invalid email for {company}")
        continue
        
    print(f"Sending to {company} ({email})...")
    success, resp = send_email(email, company)
    
    if success:
        print(f"  [OK] Sent! ID: {resp.get('id')}")
        # Update status
        supabase.table('leads').update({'status': 'contacted'}).eq('id', lead['id']).execute()
    else:
        print(f"  [FAIL] {resp}")

print("\nCampaign Complete.")
