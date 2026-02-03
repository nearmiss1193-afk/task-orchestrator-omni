import os
import sys
import requests
import json
from datetime import datetime

# Handle Windows Encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Root path for modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.vault import SovereignVault

VAULT = SovereignVault()

# GHL CONSTANTS
GHL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt"

GROK_CONTEXT = 'You are upgraded Grok 4 helping Daniel reclaim ROI for Lakeland businesses. Focus on simple 5th-grade language, "rescue" pitches, Sarah AI for leads.'

def step_1_handshake():
    print("\n--- STEP 1: Executive Handshake ---")
    headers = {"X-Sovereign-Token": VAULT.TOKEN}
    base_url = VAULT.BRIDGE_URL.rstrip('/')
    url = f"{base_url}/bridge/performance"
    
    print(f"Calling {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            funnel = data.get("funnel", {})
            print("Handshake Success!")
            print(f"Funnel: Total Leads: {funnel.get('total_leads', 'N/A')}, Active: {funnel.get('outreach_active', 'N/A')}, Positive: {funnel.get('positive_responses', 'N/A')}")
            return True
        else:
            print(f"Handshake Failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"Handshake Error: {e}")
        return False

def step_2_outreach():
    print("\n--- STEP 2: Physical Email Strike (GHL Webhook) ---")
    subject = "Test Traffic Light"
    body = (
        "🔴 Site Issue: Slow speed. Customers leave fast.\n"
        "🟡 Missing Form: Hard to contact.\n"
        "🟢 Good Reviews: Let's build on that.\n\n"
        "Fix free today?"
    )
    
    target = "nearmiss1193@gmail.com"
    print(f"Triggering GHL Webhook Strike to {target}...")
    
    payload = {
        "email": target,
        "from_name": "Daniel - Lakeland Rescue",
        "from_email": "system@aiserviceco.com",
        "subject": subject,
        "html_body": body.replace("\n", "<br>")
    }
    
    try:
        r = requests.post(GHL_WEBHOOK, json=payload, timeout=15)
        if r.status_code in [200, 201]:
            print(f"GHL Webhook Triggered Successfully. Status: {r.status_code}")
            return True
        else:
            print(f"GHL Webhook Failed: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"Outreach Error: {e}")
        return False

def step_3_grok_test():
    print("\n--- STEP 3: Upgraded Grok Integration Test ---")
    query = "Suggest 3 quick Lakeland leads for ROI rescue"
    
    if not VAULT.GROK_API_KEY:
        print("Grok Test Skipped: Missing API Key.")
        return False
        
    print(f"Checking Available Grok Models...")
    url_models = "https://api.x.ai/v1/models"
    headers = {"Authorization": f"Bearer {VAULT.GROK_API_KEY}"}
    
    try:
        r_models = requests.get(url_models, headers=headers, timeout=10)
        if r_models.status_code == 200:
            models = [m['id'] for m in r_models.json().get('data', [])]
            target_model = "grok-beta" if "grok-beta" in models else models[0]
            print(f"Using Model: {target_model}")
        else:
            print(f"Model List Failed: {r_models.status_code}. Defaulting to 'grok-beta'.")
            target_model = "grok-beta"
            
        print(f"Sending Upgraded Prompt to {target_model}...")
        url = "https://api.x.ai/v1/chat/completions"
        headers_post = {
            "Authorization": f"Bearer {VAULT.GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": target_model, 
            "messages": [
                {"role": "system", "content": GROK_CONTEXT},
                {"role": "user", "content": query}
            ],
            "temperature": 0
        }
        
        r = requests.post(url, headers=headers_post, json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            content = data['choices'][0]['message']['content']
            print(f"Grok Response: {content}")
            print("Grok Integration Verified.")
            return True
        else:
            print(f"Grok API Failed: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"Grok Error: {e}")
        return False

if __name__ == "__main__":
    print("ANTIGRAVITY v5.1 - EXECUTIVE STRIKE PROTOCOL ACTIVE")
    success = True
    if not step_1_handshake(): success = False
    if not step_2_outreach(): success = False
    if not step_3_grok_test(): success = False
    
    if success:
        print("\n🏆 MISSION SUCCESS: Execution Mode Operational. Ready for full prospecting.")
    else:
        print("\n⚠️ MISSION INCOMPLETE: Some segments failed. Check logs above.")
