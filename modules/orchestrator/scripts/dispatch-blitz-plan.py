import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

# Config
GHL_TOKEN = os.environ.get("GHL_API_TOKEN")
OWNER_CONTACT_ID = "2uuVuOP0772z7hay16og"
STRATEGY_PATH = "C:\\Users\\nearm\\.gemini\\antigravity\\brain\\d91de16e-14b7-4513-a02b-aee6e62b91d0\\blitz_strategic_overview.md"

def dispatch_blitz_plan():
    print(f"--- DISPATCHING BLITZ STRATEGY ---")
    
    if not os.path.exists(STRATEGY_PATH):
        print(f"Error: Strategy not found at {STRATEGY_PATH}")
        return

    with open(STRATEGY_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Convert Markdown to HTML for GHL Email
    # Simple replacement for images and headers
    html_content = f"<h1>Mission: Multi-Industry Blitz</h1><div style='font-family: sans-serif;'>{content.replace('# ', '<h1>').replace('## ', '<h2>').replace('!', '<br>')}"
    html_content += "</div>"

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
        "emailSubject": "[EXPANSION] Mission: Multi-Industry Blitz - 5 New Sectors",
        "html": html_content
    }

    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code in [200, 201]:
            print(f"✅ BLITZ PLAN DISPATCHED TO OWNER (GHL STATUS: {r.status_code})")
        else:
            print(f"❌ DISPATCH FAILED: {r.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    dispatch_blitz_plan()
