"""Send email drafts via Gmail API for Dan's review"""
import os
import json
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDS_FILE = 'gmail_credentials.json'
TOKEN_FILE = 'gmail_token.json'

def get_gmail_service():
    """Authenticate and return Gmail service"""
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def send_email(service, to, subject, body):
    """Send an email via Gmail API"""
    message = MIMEText(body, 'plain')
    message['to'] = to
    message['subject'] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        sent = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        print(f"✅ Email sent! Message ID: {sent['id']}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

# Email drafts
EMAILS = [
    {
        "to": "nearmiss1193@gmail.com",
        "subject": "[DRAFT 1/10] Lakeland Roofing Company - Digital Performance Audit Results",
        "body": """Dear Business Owner,

I am a local digital strategist here in Lakeland, and I've conducted a brief health audit of Lakeland Roofing Company's online presence.

To save you time, I have summarized the three critical areas that currently impact your online reputation, search ranking, and lead flow:

AREA                 STATUS              THE RISK TO THE BUSINESS
---------------------------------------------------------------------------
Search Visibility    CRITICAL (RED)      The desktop site may be failing Google's Core Web Vitals standards, acting as a 'hidden penalty' that makes it harder for homeowners to find you during storm season.

Legal Compliance     WARNING (YELLOW)    The site may be missing a dedicated Privacy Policy. Under the Florida Digital Bill of Rights, this is a mandatory requirement for businesses collecting customer data via contact forms.

Lead Efficiency      OPPORTUNITY         Currently, your team may be manually filtering every roofing inquiry. An AI-powered intake system could pre-qualify leads, ensuring your crews only spend time on high-value jobs.

THE SOLUTION: I specialize in helping roofing businesses bridge these technical gaps. I would like to offer Lakeland Roofing Company a 14-day "Intelligent Intake" trial. We can install a digital assistant on your site that "pre-screens" potential clients before they ever call your office - ensuring your team only spends time on high-value cases.

MY LOCAL GUARANTEE: Because I am a local Lakeland resident, I would like to fix your Search Visibility (Google Failure) for free this week. This will move your site back into the "Green" zone and allow you to see the quality of my work firsthand with zero risk to the business.

I'll be available to answer any questions. Feel free to reach out at your convenience.

Best regards,

Daniel Coffman
352-936-8152
Owner, AI Service Co
www.aiserviceco.com

---
[This is DRAFT 1/10 for Dan's review. Target: info@lakelandroofing.com]
"""
    }
]

if __name__ == "__main__":
    print("=" * 60)
    print("GMAIL EMAIL SENDER - Draft Review")
    print("=" * 60)
    print("\nAuthenticating with Gmail...")
    print("(A browser window will open for authorization)\n")
    
    service = get_gmail_service()
    
    # Send first email for review
    email = EMAILS[0]
    print(f"\nSending draft 1 to {email['to']}...")
    send_email(service, email['to'], email['subject'], email['body'])
    
    print("\n✅ Check your inbox at nearmiss1193@gmail.com")
    print("Reply with 'APPROVED' or changes needed.")
