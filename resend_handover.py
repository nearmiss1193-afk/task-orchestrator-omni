import os
import resend
from dotenv import load_dotenv

load_dotenv()

# Fallback Key if .env fails
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy")
resend.api_key = RESEND_API_KEY

recipient = "owner@aiserviceco.com"
sender = "onboarding@resend.dev" # Default safe sender

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {str(e)}"

print("📖 Reading Artifacts...")
capabilities = read_file(r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\EMPIRE_CAPABILITIES_MASTER.md")
recovery = read_file(r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\RECOVERY_PROTOCOL.md")

html_content = f"""
<h1>Sovereign Command: Handoff Packet</h1>
<p>Commander,</p>
<p>Per your orders, here are the vital system protocols and capabilities manifests.</p>

<hr>
<h2>1. Empire Capabilities Master</h2>
<pre style="background: #f4f4f4; padding: 10px; white-space: pre-wrap;">{capabilities[:5000]}... (truncated for email limits, see dashboard for full text)</pre>

<hr>
<h2>2. Recovery Protocol</h2>
<pre style="background: #f4f4f4; padding: 10px; white-space: pre-wrap;">{recovery}</pre>

<hr>
<p><strong>System Status:</strong> ONLINE</p>
<p><strong>Orchestrator:</strong> ACTIVE</p>
"""

print(f"📧 Sending Handover Packet to {recipient}...")

try:
    email = resend.Emails.send({
        "from": sender,
        "to": recipient,
        "subject": "Sovereign Handover: Capabilities + Recovery Protocol",
        "html": html_content
    })
    print(f"✅ Success! Email ID: {email.get('id')}")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
