import os
import resend
from dotenv import load_dotenv

# Load environment variables (including RESEND_API_KEY)
load_dotenv()
resend.api_key = os.getenv('RESEND_API_KEY')

# Paths to the files we want to include
# Paths to the files we want to include (Current Brain)
SAVE_PROTOCOL_PATH = r'C:\Users\nearm\.gemini\antigravity\brain\6ec66d63-d29a-4316-87d2-a1c21879a62a\save_protocol_report.md'
CONTACTS_PATH = r'C:\Users\nearm\.gemini\antigravity\brain\6ec66d63-d29a-4316-87d2-a1c21879a62a\contacts.md'

# Read file contents (Handle missing files gracefully)
try:
    with open(SAVE_PROTOCOL_PATH, 'r', encoding='utf-8') as f:
        save_content = f.read()
except:
    save_content = "Save Protocol Report not found."

try:
    with open(CONTACTS_PATH, 'r', encoding='utf-8') as f:
        contacts_content = f.read()
except:
    contacts_content = "Contacts list not found."

# Build email body – simple HTML with preformatted sections
html_body = f"""
<div style="text-align: center; margin-bottom: 20px;">
    <a href="http://localhost:8501" style="background-color: #007bff; color: white; padding: 15px 25px; text-decoration: none; font-size: 18px; border-radius: 5px; font-weight: bold;">🚀 Launch Mission Control</a>
    <p style="color: #666; font-size: 12px; margin-top: 5px;">(External: <a href="https://aiserviceco.com/admin">aiserviceco.com/admin</a>)</p>
</div>
<hr>
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
