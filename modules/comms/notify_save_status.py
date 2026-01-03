
import os
import resend
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
if not RESEND_API_KEY:
    print("❌ Error: RESEND_API_KEY not found in .env")
    exit(1)

resend.api_key = RESEND_API_KEY

# Protocol Paths
BASE_DIR = r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400"
PROTOCOLS = {
    "RECOVERY": os.path.join(BASE_DIR, "RECOVERY_PROTOCOL.md"),
    "CAPABILITIES": os.path.join(BASE_DIR, "EMPIRE_CAPABILITIES_MASTER.md"),
    "STRATEGY": os.path.join(BASE_DIR, "EMPIRE_EXPANSION_STRATEGY.md")
}

def read_file(path):
    try:
        if path.startswith("file:///"): path = path.replace("file:///", "")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"

def main():
    print("📧 Preparing Stakeholder Notification...")

    # 1. Gather Intelligence
    recovery_doc = read_file(PROTOCOLS["RECOVERY"])
    capabilities_doc = read_file(PROTOCOLS["CAPABILITIES"])
    strategy_doc = read_file(PROTOCOLS["STRATEGY"])

    # 2. Construct Email Body (HTML)
    email_body = f"""
    <h1>💾 Sovereign System: Save Protocol Executed</h1>
    <p>The system has been successfully backed up and deployed.</p>
    
    <hr>
    <h2>1. Recovery Protocol</h2>
    <pre style="background: #f4f4f4; padding: 10px; white-space: pre-wrap;">{recovery_doc[:15000]}</pre>

    <hr>
    <h2>2. Capabilities Snapshot</h2>
    <pre style="background: #f4f4f4; padding: 10px; white-space: pre-wrap;">{capabilities_doc[:15000]}</pre>

    <hr>
    <h2>3. Strategic Recommendations</h2>
    <p>Extracted from Expansion Strategy:</p>
    <pre style="background: #f4f4f4; padding: 10px; white-space: pre-wrap;">{strategy_doc[:15000]}</pre>

    <hr>
    <p><strong>Status:</strong> 🟢 LIVE & SECURE</p>
    <p><em>Empire Sovereign Cloud Autopilot</em></p>
    """

    # 3. Send via Resend
    recipients = ["nearmiss1193@gmail.com", "owner@aiserviceco.com"]
    
    try:
        r = resend.Emails.send({
            "from": "alert@aiserviceco.com",
            "to": recipients,
            "subject": "💾 System Save: Protocols & Status Update",
            "html": email_body
        })
        print(f"✅ Notification Sent to {recipients}. ID: {r.get('id')}")
    except Exception as e:
        print(f"❌ Email Failed: {e}")

if __name__ == "__main__":
    main()
