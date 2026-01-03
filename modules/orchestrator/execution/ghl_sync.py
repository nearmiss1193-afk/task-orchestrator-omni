import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

def sync_all_35_leads():
    files = [
        "execution/leads_miami.json", 
        "execution/leads_los_angeles.json",
        "execution/enriched_batch_50.json",
        "execution/enriched_batch_100.json"
    ]
    
    token = os.environ.get("GHL_API_TOKEN")
    location_id = os.environ.get("GHL_LOCATION_ID")
    
    if not token or not location_id:
        print("❌ ERROR: GHL_API_TOKEN or GHL_LOCATION_ID missing from .env.local")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    # Fetch mapping
    mapping = {}
    try:
        res = requests.get(f"https://services.leadconnectorhq.com/locations/{location_id}/customFields", headers=headers)
        if res.status_code == 200:
            fields = res.json().get("customFields", [])
            for f in fields:
                if f['name'] == "Annual Loss Projection":
                    mapping["annual_loss"] = f['id']
                if f['name'] == "Vortex Audit Link":
                    mapping["audit_link"] = f['id']
    except Exception as e:
        print(f"⚠️ Mapping error: {e}")

    annual_loss_id = mapping.get("annual_loss", "W1QYZJ7ooiUtDiNmf9Xi") # Fallback to verified ID
    audit_link_id = mapping.get("audit_link", "JVka1qNEbJmPL4z31H1a")   # Fallback to verified ID

    all_leads = []
    for f_path in files:
        if os.path.exists(f_path):
            with open(f_path, "r") as f:
                all_leads.extend(json.load(f))
    
    print(f"🔥 TOTAL LEADS FOR LIVE SYNC: {len(all_leads)}")
    
    for lead in all_leads:
        # Construct GHL Payload
        payload = {
            "name": lead["name"],
            "email": f"info@{lead['website']}", 
            "locationId": location_id,
            "tags": ["trigger-vortex", "spartan-strike", lead.get("niche", "general")],
            "customFields": [
                {"id": annual_loss_id, "value": f"${lead.get('annual_loss', 0):,}"},
                {"id": audit_link_id, "value": lead.get("website", "")}
            ]
        }
        
        try:
            res = requests.post("https://services.leadconnectorhq.com/contacts/", json=payload, headers=headers)
            if res.status_code in [200, 201]:
                print(f"✅ SYNCED: {lead['name']} -> GHL. Outreach Triggered.")
            else:
                print(f"⚠️ FAILED SYNC: {lead['name']} ({res.status_code})")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    sync_all_35_leads()
