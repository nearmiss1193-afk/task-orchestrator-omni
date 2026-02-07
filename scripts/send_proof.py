
import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configuration
TOKEN_PATH = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_token.json"
RECIPIENT = "nearmiss1193@gmail.com"
SUBJECT = "PROOF DB: Optum RX + Contact Form Updates"
HTML_PATH = r"C:\Users\nearm\.gemini\antigravity\brain\0b97dae9-c5c0-4924-8d97-793b59319985\batch3_email1_html.html"

def get_gmail_service():
    """Get authenticated Gmail service using existing token."""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token not found at {TOKEN_PATH}")
        
    with open(TOKEN_PATH, "r") as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"]
    )
    return build("gmail", "v1", credentials=creds)

def send_proof():
    try:
        service = get_gmail_service()
        
        # Read HTML
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # PROOF HEADER
        header = f"""
        <div style="background-color: #ffffd0; padding: 10px; margin-bottom: 20px; border: 2px solid #ffcc00; font-family: sans-serif;">
            <strong>🛑 PROOF MODE</strong><br>
            This is a preview of the HTML email template.<br>
            <strong>Subject:</strong> {SUBJECT}
        </div>
        """
        full_body = header + html_content

        # Create Message
        msg = MIMEMultipart()
        msg['to'] = RECIPIENT
        msg['from'] = "AI Service Co Proof <owner@aiserviceco.com>"
        msg['subject'] = SUBJECT
        msg.attach(MIMEText(full_body, 'html'))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        print(f"Sending proof to {RECIPIENT}...")
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        print("✅ Proof Email Sent Successfully (via Gmail API).")

    except Exception as e:
        print(f"❌ Failed to send: {e}")

if __name__ == "__main__":
    send_proof()
