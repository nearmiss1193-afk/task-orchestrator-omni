"""
Send Individual Email Previews for Owner Approval
Each email sent separately with PDF attachment - exactly as customer will receive

// turbo-all
"""
import os
import sys
sys.path.insert(0, '.')

from datetime import datetime

# Check for google auth libraries
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run(["pip", "install", "google-auth-oauthlib", "google-api-python-client"], check=True)
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Gmail API Setup
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE = 'gmail_token.json'
CREDENTIALS_FILE = 'gmail_credentials.json'

# Owner email for preview
OWNER_EMAIL = "nearmiss1193@gmail.com"

# Email batches to send for preview
EMAILS_TO_PREVIEW = [
    {
        "subject": "[PREVIEW] Brilliant Smiles Lakeland - Digital Performance Audit Results",
        "to_name": "Dr. Parmar",
        "business": "Brilliant Smiles Lakeland",
        "website": "yourlakelanddentist.com",
        "industry": "Dental",
        "actual_recipient": "info@yourlakelanddentist.com",
        "pdf": "email_attachments/batch3/Audit_Brilliant_Smiles_Lakeland.pdf"
    }
]


def get_gmail_service():
    """Get authenticated Gmail API service"""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("ERROR: Need to authenticate with Google first!")
            return None
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def create_email_body(to_name: str, business: str, website: str, industry: str) -> str:
    """Create the actual email body in bfisher format - PLAIN TEXT"""
    
    return f"""Dear {to_name},

I am a local digital strategist here in Lakeland, and I've conducted a brief health audit of {business}'s online presence.

To save you time, I have summarized the three critical areas that currently impact your online reputation, search ranking, and lead flow:

AREA                 STATUS              THE RISK TO THE BUSINESS
---------------------------------------------------------------------------
Search Visibility    CRITICAL (RED)      The site may be failing Google's Core Web Vitals standards, creating a 'hidden penalty' that makes it harder for customers to find you.

Legal Compliance     WARNING (YELLOW)    The site may be missing a dedicated Privacy Policy. Under the Florida Digital Bill of Rights, this is a mandatory requirement for businesses collecting customer data.

Lead Efficiency      OPPORTUNITY         Currently, your staff may be manually fielding every inquiry. An intelligent intake system could pre-screen calls, ensuring your team only responds to qualified service calls.

THE SOLUTION: I specialize in helping {industry} businesses bridge these technical gaps. I would like to offer {business} a 14-day "Intelligent Intake" trial. We can install a digital assistant that "pre-screens" potential clients before they call - ensuring your team only spends time on high-value cases.

MY LOCAL GUARANTEE: Because I am a local Lakeland resident, I would like to fix your Search Visibility (Google Failure) for free this week. This will move your site back into the "Green" zone and allow you to see the quality of my work firsthand with zero risk.

I have attached your full Performance Report. I will follow up with your office in an hour to see if you have any questions.

Best regards,

Daniel Coffman
352-936-8152
Owner, AI Service Co
www.aiserviceco.com
"""


def create_email_message(email_data: dict, is_preview: bool = True) -> MIMEMultipart:
    """Create email message with attachment"""
    
    msg = MIMEMultipart('mixed')
    
    if is_preview:
        # For preview: send to Dan with PREVIEW tag
        msg['Subject'] = email_data['subject']
        msg['From'] = "Daniel Coffman <owner@aiserviceco.com>"
        msg['To'] = OWNER_EMAIL
        
        # Add preview header showing actual recipient
        preview_header = f"--- PREVIEW MODE ---\nThis email will be sent TO: {email_data['actual_recipient']}\n--- END PREVIEW ---\n\n"
        body = preview_header + create_email_body(
            email_data['to_name'],
            email_data['business'],
            email_data['website'],
            email_data['industry']
        )
    else:
        # For production: send to actual recipient
        msg['Subject'] = f"{email_data['business']} - Digital Performance Audit Results"
        msg['From'] = "Daniel Coffman <owner@aiserviceco.com>"
        msg['To'] = email_data['actual_recipient']
        body = create_email_body(
            email_data['to_name'],
            email_data['business'],
            email_data['website'],
            email_data['industry']
        )
    
    # Attach plain text body
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF if exists
    pdf_path = email_data.get('pdf', '')
    if pdf_path and os.path.exists(pdf_path):
        filename = os.path.basename(pdf_path)
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'pdf')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
            print(f"   📎 Attached: {filename}")
    else:
        print(f"   ⚠️ No PDF found: {pdf_path}")
    
    return msg


def send_email(service, message) -> dict:
    """Send email via Gmail API"""
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        sent = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return {"success": True, "message_id": sent['id']}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("=" * 70)
    print("SENDING INDIVIDUAL EMAIL PREVIEWS FOR OWNER APPROVAL")
    print(f"Sending to: {OWNER_EMAIL}")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 70)
    
    # Get Gmail service
    print("\n[1] Authenticating with Gmail API...")
    service = get_gmail_service()
    if not service:
        print("❌ Failed to authenticate!")
        return
    print("   ✅ Authenticated!")
    
    # Send each preview email
    sent_count = 0
    failed_count = 0
    
    for i, email_data in enumerate(EMAILS_TO_PREVIEW, 1):
        print(f"\n[{i}/{len(EMAILS_TO_PREVIEW)}] Sending: {email_data['subject']}")
        
        # Create message
        msg = create_email_message(email_data, is_preview=True)
        
        # Send
        result = send_email(service, msg)
        
        if result['success']:
            print(f"   ✅ Sent! ID: {result['message_id']}")
            sent_count += 1
        else:
            print(f"   ❌ Failed: {result['error']}")
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("PREVIEW EMAILS SENT")
    print("=" * 70)
    print(f"✅ Sent: {sent_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"\nCheck your inbox: {OWNER_EMAIL}")
    print("\nReply with APPROVE to send these to actual recipients.")
    print("=" * 70)


if __name__ == "__main__":
    main()
