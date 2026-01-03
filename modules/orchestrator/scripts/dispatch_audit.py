import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

# Config
GHL_TOKEN = os.environ.get("GHL_API_TOKEN")
OWNER_CONTACT_ID = "2uuVuOP0772z7hay16og"
REPORT_PATH = "C:/Users/nearm/.gemini/antigravity/brain/d91de16e-14b7-4513-a02b-aee6e62b91d0/mission_impact_report.md"

def dispatch_audit():
    print(f"--- DISPATCHING MISSION AUDIT ---")
    
    if not os.path.exists(REPORT_PATH):
        print(f"Error: Report not found at {REPORT_PATH}")
        return

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Simple Markdown to HTML conversion
    html_content = f"""
    <div style='font-family: sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px;'>
        <h1 style='color: #2c3e50;'>Mission Impact Report: Quantified Results</h1>
        <pre style='background: #f4f4f4; padding: 15px; white-space: pre-wrap;'>{content}</pre>
    </div>
    """

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
        "emailSubject": "[AUDIT] Mission Impact Report: Quantified Results",
        "html": html_content
    }

    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code in [200, 201]:
            print(f"✅ AUDIT REPORT DISPATCHED TO OWNER (GHL STATUS: {r.status_code})")
        else:
            print(f"❌ DISPATCH FAILED: {r.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    dispatch_audit()
