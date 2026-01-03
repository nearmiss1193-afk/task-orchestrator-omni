import os
import json
import requests
import time
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(".env.local")

# Config
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
GHL_API_KEY = os.environ.get("GHL_API_KEY") # This might be the Location ID or API Key
OWNER_EMAIL = "owner@aiserviceco.com"

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def launch_outreach():
    supabase = get_supabase()
    
    # 1. Fetch enriched leads
    print("--- MISSION: REVENUE LAUNCH (SCALED) ---")
    leads = supabase.table("contacts_master").select("*").or_("ghl_contact_id.ilike.millen_%,ghl_contact_id.ilike.fl_blit_%,ghl_contact_id.ilike.blitz_%,ghl_contact_id.ilike.mission_fs_%,ghl_contact_id.ilike.smb_tampa_%").eq("status", "research_done").execute()
    
    if not leads.data:
        print("No enriched leads found. Run enrichment first.")
        return

    print(f"Found {len(leads.data)} leads ready for outreach.")

    for lead in leads.data:
        contact_id = lead['ghl_contact_id']
        hook = lead.get('ai_strategy', "saw your site. good hustle but you're leaking leads.")
        name = lead.get('full_name', 'Founder')
        
        print(f"\n🚀 Launching outreach for {name} ({contact_id})...")
        print(f"Hook: {hook}")

        # MISSION: LIVE CC OWNER VIA GHL
        vortex_url = "https://ghl-vortex.demo/special-invite"
        email_body = f"<h1>Spartan Outreach CC</h1><p><b>To:</b> {lead.get('email')}</p><p><b>Subject:</b> Quick thought for {name}</p><p><b>Body:</b> hey {name.split()[0].lower()}, {hook}</p><p><b>[OFFER_PAGE]:</b> {vortex_url}</p>"
        
        url = "https://services.leadconnectorhq.com/conversations/messages"
        ghl_token = os.environ.get("GHL_API_TOKEN")
        headers = {'Authorization': f'Bearer {ghl_token}', 'Version': '2021-07-28', 'Content-Type': 'application/json'}
        payload = {
            "type": "Email",
            "contactId": "2uuVuOP0772z7hay16og", # Owner Contact ID
            "emailFrom": "system@aiserviceco.com",
            "emailSubject": f"Outreach CC: {name}",
            "html": email_body
        }
        try:
            r = requests.post(url, json=payload, headers=headers)
            print(f"✅ CC DISPATCHED TO OWNER (GHL STATUS: {r.status_code})")
        except:
            print("❌ CC DISPATCH FAILED")
        
        # MISSION: LIVE PROSPECT OUTREACH VIA GHL (NO SIMULATION)
        prospect_payload = {
            "type": "Email",
            "contactId": contact_id,
            "emailFrom": "system@aiserviceco.com",
            "emailSubject": f"Quick thought for {name}",
            "html": f"<p>hey {name.split()[0].lower()}, {hook}</p><p><b>[OFFER_PAGE]:</b> {vortex_url}</p>"
        }
        try:
            r_prospect = requests.post(url, json=prospect_payload, headers=headers)
            print(f"✅ PROSPECT OUTREACH SENT (GHL STATUS: {r_prospect.status_code})")
        except:
            print("❌ PROSPECT OUTREACH FAILED")
        
        supabase.table("contacts_master").update({
            "status": "outreach_sent"
        }).eq("ghl_contact_id", contact_id).execute()
        
        print(f"✅ Lead {contact_id} marked as ACTIVE in outreach pipeline.")
        
        time.sleep(2) # Spartan pacing

    print("\n--- MISSION COMPLETE: ALL LEADS LIVE ---")

if __name__ == "__main__":
    launch_outreach()
