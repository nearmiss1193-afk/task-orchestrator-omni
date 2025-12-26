import os
import json
import time
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from nurture_config import NURTURE_TEMPLATES, VORTEX_DEMO_URL

load_dotenv(".env.local")

# Config
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
OWNER_EMAIL = "owner@aiserviceco.com"

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_interest(raw_research: str, category: str) -> str:
    # A simple mapping for now, keeping it robust
    if not raw_research or not isinstance(raw_research, str):
        return f"reliable {category} service"
    
    # Simple logic: pick a common keyword or use AI (simulated here for speed)
    interests = ["emergency response", "online booking", "customer satisfaction", "technical expertise", "fast dispatch"]
    for interest in interests:
        if interest in raw_research.lower():
            return interest
    return f"optimizing your {category} lead flow"

def execute_nurture():
    supabase = get_supabase()
    
    # Fetch leads in 'outreach_sent' or previous nurture stages
    # Mission: SMB Expansion leads
    leads = supabase.table("contacts_master").select("*").ilike("ghl_contact_id", "smb_tampa_%").execute()
    
    print(f"--- AUTHORITY LOOP: NURTURE EXECUTION ---")
    
    for lead in leads.data:
        contact_id = lead.get('ghl_contact_id')
        status = lead.get('status') or "new"
        created_at_raw = lead.get('created_at')
        if not created_at_raw:
            print(f"Lead {contact_id}: Missing created_at")
            continue
        created_at = datetime.datetime.fromisoformat(created_at_raw.replace('Z', '+00:00'))
        days_since_start = (datetime.datetime.now(datetime.timezone.utc) - created_at).days
        
        # Logic: 
        # Outreach Sent (Day 0)
        # Nurture Day 3
        # Nurture Day 10
        # Nurture Day 20
        
        target_stage = None
        if status == "outreach_sent" and days_since_start >= 3:
            target_stage = "day_3"
        elif status == "nurture_day_3" and days_since_start >= 10:
            target_stage = "day_10"
        elif status == "nurture_day_10" and days_since_start >= 20:
            target_stage = "day_20"

        if not target_stage:
            print(f"Lead {contact_id}: No nurture due (Day {days_since_start})")
            continue

        # Prepare Template
        template = NURTURE_TEMPLATES[target_stage]
        full_name = lead.get('full_name') or "Founder"
        category = "HVAC" if "hvac" in full_name.lower() or "ac" in full_name.lower() else "Service"
        if "plumb" in full_name.lower(): category = "Plumbing"
        if "roof" in full_name.lower(): category = "Roofing"
        
        interest = extract_interest(lead.get('raw_research', ""), category)
        
        # Fill placeholders
        name = full_name.split()[0]
        subject = template['subject'].replace("[Category]", category).replace("[Company]", full_name).replace("[Name]", name)
        body = template['body'].replace("[Name]", name).replace("[Category]", category).replace("[Company]", full_name).replace("[Interest]", interest)
        body = body.replace("[Trigger_Link]", VORTEX_DEMO_URL).replace("[Spartan_Logo_Link]", "| Spartan AI Admin |")
        
        print(f"\n🚀 Sending NURTURE {target_stage.upper()} to {lead['full_name']}...")
        print(f"Subject: {subject}")
        print(f"Interest matched: {interest}")

        # MISSION: LIVE CC OWNER VIA GHL (MISSION 8)
        email_body = f"<h1>Spartan Nurture CC</h1><p><b>Lead:</b> {contact_id} ({target_stage})</p><p><b>Message Content:</b> {body}</p><p><b>[OFFER_PAGE]:</b> {VORTEX_DEMO_URL}</p>"
        
        url = "https://services.leadconnectorhq.com/conversations/messages"
        ghl_token = os.environ.get("GHL_API_TOKEN")
        headers = {'Authorization': f'Bearer {ghl_token}', 'Version': '2021-07-28', 'Content-Type': 'application/json'}
        payload = {
            "type": "Email",
            "contactId": "2uuVuOP0772z7hay16og", # Owner Contact ID
            "emailFrom": "system@aiserviceco.com",
            "emailSubject": f"Nurture CC: {contact_id}",
            "html": email_body
        }
        try:
            r = requests.post(url, json=payload, headers=headers)
            print(f"✅ NURTURE CC DISPATCHED (GHL STATUS: {r.status_code})")
        except:
            print("❌ NURTURE CC FAILED")

        # MISSION: LIVE NURTURE MESSAGE TO PROSPECT (NO SIMULATION)
        prospect_nurture_payload = {
            "type": "Email",
            "contactId": contact_id,
            "emailFrom": "system@aiserviceco.com",
            "emailSubject": subject,
            "html": body
        }
        try:
            r_prospect = requests.post(url, json=prospect_nurture_payload, headers=headers)
            print(f"✅ NURTURE SENT TO PROSPECT (GHL STATUS: {r_prospect.status_code})")
        except:
            print("❌ NURTURE SEND FAILED")

        # Update Status
        supabase.table("contacts_master").update({
            "status": f"nurture_{target_stage}"
        }).eq("ghl_contact_id", contact_id).execute()
        
        print(f"✅ Lead {contact_id} advanced to {target_stage}")

    print("\n--- NURTURE LOOP COMPLETE ---")

if __name__ == "__main__":
    execute_nurture()
