import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv(".env.local")

def send_email(subject, body):
    token = os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")
    # Owner contact ID from deploy.py or user context
    contact_id = "2uuVuOP0772z7hay16og" # Hardcoded from deploy.py logic
    
    url = "https://services.leadconnectorhq.com/conversations/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-04-15",
        "Content-Type": "application/json"
    }
    
    payload = {
        "type": "Email",
        "contactId": contact_id,
        "emailSubject": subject,
        "html": f"<div style='white-space: pre-wrap; font-family: monospace;'>{body}</div>"
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            print(f"✅ Sent: {subject}")
        else:
            print(f"❌ Failed: {res.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_handoff_email():
    print("📧 PREPARING HANDOFF EMAIL PACKAGE...")
    
    artifacts = {
        "System Manual": r"C:\Users\nearm\.gemini\antigravity\brain\4f7b1359-6cfe-4369-a4cd-ac610e638bc9\system_manual.md",
        "Handoff Report": r"C:\Users\nearm\.gemini\antigravity\brain\4f7b1359-6cfe-4369-a4cd-ac610e638bc9\handoff_report.md",
        "Walkthrough": r"C:\Users\nearm\.gemini\antigravity\brain\4f7b1359-6cfe-4369-a4cd-ac610e638bc9\walkthrough.md"
    }
    
    full_body = "<h1>EMPIRE UNIFIED - FINAL HANDOFF</h1><p>Here are your system documents.</p><hr>"
    
    for title, path in artifacts.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                full_body += f"<h2>{title}</h2><pre>{content}</pre><hr>"
        else:
            print(f"⚠️ Missing: {path}")

    send_email("Empire Unified: Complete System Handoff Package", full_body)

if __name__ == "__main__":
    run_handoff_email()
