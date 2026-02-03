import os
import requests
from dotenv import load_dotenv

# Absolute path to .env.local
env_path = r"c:\Users\nearm\.gemini\antigravity\scratch\task-orchestrator\.env.local"
load_dotenv(env_path)

def audit_workflows():
    token = os.environ.get("GHL_API_TOKEN")
    location_id = os.environ.get("GHL_LOCATION_ID")
    
    if not token or not location_id:
        print(f"❌ ERROR: Missing credentials. Checked {env_path}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28"
    }

    # GHL Workflows Endpoint
    url = f"https://services.leadconnectorhq.com/workflows/?locationId={location_id}"
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            workflows = res.json().get("workflows", [])
            print(f"📋 Auditing {len(workflows)} workflows for 'trigger-vortex'...")
            
            found_vortex = False
            for wf in workflows:
                wf_id = wf.get('id')
                wf_name = wf.get('name')
                
                # Fetch detailed workflow to see triggers
                # Note: This is a guess on the v2 detail endpoint based on naming conventions
                detail_url = f"https://services.leadconnectorhq.com/workflows/{wf_id}"
                detail_res = requests.get(detail_url, headers=headers)
                
                if detail_res.status_code == 200:
                    wf_data = detail_res.json().get('workflow', {})
                    triggers = wf_data.get('triggers', [])
                    for t in triggers:
                        if t.get('type') == 'contact_tag' and 'trigger-vortex' in str(t.get('filters', [])):
                            print(f"🎯 FOUND: {wf_name} is triggered by 'trigger-vortex'!")
                            found_vortex = True
                            break
                else:
                    # If detail endpoint fails, we just log the name
                    print(f"- {wf_name} (Unable to audit triggers)")
            
            if not found_vortex:
                print("❌ RESULT: No workflow found matching 'trigger-vortex' tag trigger.")
        else:
            print(f"❌ API Error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    audit_workflows()
