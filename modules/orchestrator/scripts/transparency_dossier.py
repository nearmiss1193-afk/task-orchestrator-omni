import os
import json
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(".env.local")

# Config
GHL_TOKEN = os.environ.get("GHL_API_TOKEN")
OWNER_CONTACT_ID = "2uuVuOP0772z7hay16og"
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def send_dossier():
    supabase = get_supabase()
    print("--- GENERATING TRANSPARENCY DOSSIER ---")
    
    # 1. Fetch outreach status
    leads = supabase.table("contacts_master").select("*").or_("ghl_contact_id.ilike.mission_fs_%,ghl_contact_id.ilike.smb_tampa_%").execute()
    
    html_content = "<h1>Mission Transparency Dossier</h1>"
    html_content += "<p>Below is the record of all outreach and nurture touches sent to prospects, including localized ad assets.</p>"

    # 2. Ads Section
    html_content += "<h2>1. Mission: Visibility (Ad Leads & Assets)</h2>"
    html_content += "<ul>"
    html_content += "<li><b>Meta Ad Demo</b>: <a href='https://ghl-vortex.demo/ad-preview-meta'>Tampa HVAC Automation</a></li>"
    html_content += "<li><b>Google Keyword Target</b>: 'hvac lead gen tampa'</li>"
    html_content += "<li><b>Offer Page Link</b>: <a href='https://ghl-vortex.demo/special-invite'>Vortex Priority Invite</a></li>"
    html_content += "</ul>"

    # 3. Prospect Outreach Section
    html_content += "<h2>2. Active Prospect Outreach Record</h2>"
    html_content += "<table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%; border: 1px solid #ddd;'>"
    html_content += "<tr style='background-color: #f2f2f2;'><th>Lead Name</th><th>Status</th><th>Last Message (AI Draft)</th></tr>"
    
    for lead in leads.data:
        name = lead.get('full_name', 'Unknown')
        status = lead.get('status', 'new')
        hook = lead.get('ai_strategy', 'N/A')
        
        html_content += f"<tr><td>{name}</td><td>{status}</td><td>{hook}</td></tr>"
    
    html_content += "</table>"

    html_content += "<p><i>Note: Every future message from these leads will trigger an immediate SMS and Email alert to you.</i></p>"

    # 4. Dispatch via GHL
    url = "https://services.leadconnectorhq.com/conversations/messages"
    headers = {
        'Authorization': f'Bearer {GHL_TOKEN}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json'
    }
    payload = {
        "type": "Email",
        "contactId": OWNER_CONTACT_ID,
        "emailFrom": "system@aiserviceco.com",
        "emailSubject": "[DOSSIER] Complete Outreach & Ad Transparency Report",
        "html": html_content
    }

    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code in [200, 201]:
            print(f"✅ DOSSIER DISPATCHED TO OWNER (GHL STATUS: {r.status_code})")
        else:
            print(f"❌ DISPATCH FAILED: {r.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_dossier()
