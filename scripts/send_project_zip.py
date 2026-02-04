import os
import resend
import base64
from dotenv import load_dotenv

load_dotenv()

def send_project_zip(zip_path):
    resend.api_key = os.environ.get("RESEND_API_KEY")
    recipient = "nearmiss1193@gmail.com"
    
    if not os.path.exists(zip_path):
        print(f"❌ Zip file not found: {zip_path}")
        return

    print(f"📧 Preparing to send: {zip_path}")
    
    with open(zip_path, "rb") as f:
        content = f.read()
        encoded = base64.b64encode(content).decode()

    try:
        params = {
            "from": "Sovereign AI <automation@aiserviceco.com>",
            "to": [recipient],
            "subject": "FULL PROJECT ZIP – FOR ARA",
            "html": "<p>Here’s everything. Check the drift, fix the site, give me back clean code.</p>",
            "attachments": [
                {
                    "filename": os.path.basename(zip_path),
                    "content": encoded,
                }
            ],
        }

        email = resend.Emails.send(params)
        print(f"✅ ZIP SENT – {email['id']} – FILE SIZE: {len(content)/1024/1024:.2f} MB")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    send_project_zip("aiserviceco-full-project-v1.zip")

token: `sov-audit-2026-ghost`
