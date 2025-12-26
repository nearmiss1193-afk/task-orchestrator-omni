
import os
import requests
import json
from supabase import create_client, Client

def load_env():
    env_path = ".env.local"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        os.environ[parts[0]] = parts[1]

load_env()

SUB_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
GHL_TOKEN = os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")

def get_supabase() -> Client:
    return create_client(SUB_URL, SUB_KEY)

def turbo_dispatch():
    print("🚀 MISSION: TURBO ACCEPT & DISPATCH")
    supabase = get_supabase()
    
    # 1. Look for all leads that are research_done and not yet nurtured
    try:
        # We'll fetch all leads and filter in python to be safe against schema quirks
        res = supabase.table("contacts_master").select("*").execute()
        leads = res.data
    except Exception as e:
        print(f"❌ Supabase Error: {str(e)}")
        return

    if not leads:
        print("✅ No leads found in database.")
        return

    # Filter for Empire Scaling leads that are ready
    ready_leads = [l for l in leads if l.get("status") == "research_done"]
    
    print(f"📊 Total Leads: {len(leads)}")
    print(f"🎯 Ready for Outreach: {len(ready_leads)}")

    if not ready_leads:
        print("✅ No leads currently in 'research_done' state.")
        return

    print(f"🌊 Starting Wave Dispatch for {len(ready_leads)} leads...")

    for lead in ready_leads:
        cid = lead.get("ghl_contact_id")
        name = lead.get("full_name", "Founder")
        hook = lead.get("ai_strategy", "noticed your missed call automation could be improved.")
        email = lead.get("email")
        
        if not cid: continue

        print(f"📤 Dispatching to {name} ({cid})...")

        # GHL Payload
        ghl_url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {
            "Authorization": f"Bearer {GHL_TOKEN}",
            "Version": "2021-04-15",
            "Content-Type": "application/json"
        }
        
        # A/B Style logic
        subject = f"Question for {name.split()[0]}" if name else "Quick Question"
        body = f"Hi {name.split()[0] if name else 'there'},\n\n{hook}\n\nI built a quick breakdown for your missed call ROI here: https://link.aiserviceco.com/audit\n\n- Spartan"
        
        payload = {
            "type": "Email",
            "contactId": cid,
            "subject": subject,
            "html": f"<p>{body.replace('\n', '<br>')}</p>"
        }

        try:
            r = requests.post(ghl_url, json=payload, headers=headers)
            if r.status_code in [200, 201]:
                print(f"✅ Sent to {cid}")
                supabase.table("contacts_master").update({"status": "outreach_sent"}).eq("ghl_contact_id", cid).execute()
            else:
                print(f"⚠️ GHL Error for {cid}: {r.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print("🏁 Turbo Dispatch Complete.")

if __name__ == "__main__":
    turbo_dispatch()
