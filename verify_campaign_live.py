
import modal
import deploy
import os
import requests
import json
import random

app = deploy.app

@app.local_entrypoint()
def main():
    print("🚀 LIVE FIRE VERIFICATION (TARGET: OWNER) 🚀")
    res = verify_live.remote()
    print("\n--- CAMPAIGN PREVIEW ---")
    print(res)

@app.function(image=deploy.image, secrets=[deploy.VAULT])
def verify_live():
    supabase = deploy.get_supabase()
    
    # 1. Fetch Real Lead Data (Simulation Source)
    # We grab a 'research_done' lead to get a REAL hook/name
    res = supabase.table("contacts_master").select("*").eq("status", "research_done").limit(10).execute()
    real_leads = res.data
    
    if not real_leads:
        return "❌ No 'research_done' leads found to simulate with. Run 'manual_ghl_sync' or 'research_lead_logic' first."

    # Pick a random real lead to impersonate the CONTENT source
    lead = random.choice(real_leads)
    
    # 2. Config (Target: YOU)
    owner_id = "2uuVuOP0772z7hay16og"
    
    # 3. Message Construction (Using Real Data)
    
    full_name = lead.get('full_name', 'Business Owner')
    first_name = full_name.split()[0]
    
    # AI Research Hook
    raw_research = lead.get('raw_research', {}) or {}
    hook = raw_research.get('hook') or lead.get('ai_strategy') or "saw your contact form is generic."
    
    # NEW STRONGER CALL TO ACTION
    audit_link = "https://link.aiserviceco.com/audit" 
    
    # A. EMAIL BODY
    email_subject = f"question re: {full_name}'s site"
    email_body = (
        f"hey {first_name.lower()},\n\n"
        f"{hook}\n\n"
        f"i recorded a 30s screen-share showing exactly where the drop-off is occurring.\n\n"
        f"watch here: {audit_link}\n\n"
        f"- Spartan"
    )

    # B. SMS BODY (Value Driven)
    sms_body = (
        f"hey {first_name.lower()}, {hook} "
        f"i made a 30s video showing the fix: {audit_link} "
        f"- spartan"
    )

    # 4. Auth (Reality Protocol)
    token = os.environ.get("GHL_AGENCY_API_TOKEN") 
    loc = os.environ.get("GHL_LOCATION_ID")
    headers = {
        'Authorization': f'Bearer {token}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json',
        'Location-Id': loc
    }
    
    url = "https://services.leadconnectorhq.com/conversations/messages"
    logs = []
    
    logs.append(f"🎯 SIMULATING FOR REAL PROSPECT: {full_name}")
    logs.append(f"🪝 HOOK: {hook}")
    
    try:
        # SEND EMAIL (To Owner)
        e_payload = {
            "type": "Email", "contactId": owner_id, 
            "emailFrom": "system@aiserviceco.com",
            "emailSubject": email_subject,
            "html": f"<p>{email_body.replace(chr(10), '<br>')}</p>"
        }
        r_e = requests.post(url, json=e_payload, headers=headers)
        logs.append(f"✉️ EMAIL STATUS: {r_e.status_code}")
        
        # SEND SMS (To Owner)
        s_payload = {"type": "SMS", "contactId": owner_id, "message": sms_body}
        r_s = requests.post(url, json=s_payload, headers=headers)
        logs.append(f"📱 SMS STATUS: {r_s.status_code}")
        
        if r_s.status_code not in [200, 201]:
            logs.append(f"   SMS Error: {r_s.text}")

    except Exception as e:
        logs.append(f"❌ EXECUTION ERROR: {e}")
        
    return "\n".join(logs)
