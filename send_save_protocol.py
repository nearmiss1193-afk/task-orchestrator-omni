import os
import resend
from dotenv import load_dotenv

# Load environment variables (including RESEND_API_KEY)
load_dotenv()
resend.api_key = os.getenv('RESEND_API_KEY')

# Paths to the files we want to include
SAVE_PROTOCOL_PATH = r'c:\Users\nearm\.gemini\antigravity\brain\63118102-5d19-4071-98e0-4bcad0b36f9b\save_protocol_report.md'
CONTACTS_PATH = r'c:\Users\nearm\.gemini\antigravity\brain\63118102-5d19-4071-98e0-4bcad0b36f9b\contacts.md'

# Read file contents
with open(SAVE_PROTOCOL_PATH, 'r', encoding='utf-8') as f:
    save_content = f.read()
with open(CONTACTS_PATH, 'r', encoding='utf-8') as f:
    contacts_content = f.read()

# Build email body – simple HTML with preformatted sections
html_body = f"""
<h2>📋 Save Protocol Report</h2>
<pre style='background:#f4f4f4;padding:10px;border-radius:5px;'>{save_content}</pre>
<h2>📇 Contact List</h2>
<pre style='background:#f4f4f4;padding:10px;border-radius:5px;'>{contacts_content}</pre>
"""

# Email parameters – send to both addresses
params = {
    "from": "alert@aiserviceco.com",
    "to": ["nearmiss1193@gmail.com", "owner@aiserviceco.com"],
    "subject": "🚀 Save Protocol & Contacts – Empire Unified",
    "html": html_body,
}

try:
    email = resend.Emails.send(params)
    print("✅ Email sent successfully")
    print(email)
except Exception as e:
    print(f"❌ Failed to send email: {e}")
