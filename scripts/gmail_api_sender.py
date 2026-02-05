"""
Gmail Email Sender - bfisher Format
Proper email format per operational memory standards

// turbo-all
"""
import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path

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
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Files
CREDENTIALS_FILE = 'gmail_credentials.json'
TOKEN_FILE = 'gmail_token.json'

def get_gmail_service():
    """Get authenticated Gmail API service"""
    creds = None
    
    # Check for existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, need to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Need to authenticate with Google...")
            print("A browser window will open for authentication.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the token for future runs
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print(f"Token saved to {TOKEN_FILE}")
    
    return build('gmail', 'v1', credentials=creds)


def create_bfisher_email(
    to_email: str,
    business_name: str,
    contact_name: str,
    website: str,
    industry: str,
    city: str,
    load_time: str = "13.7",
    page_weight: str = "6.4MB",
    attachment_paths: list = None
) -> MIMEMultipart:
    """
    Create email in bfisher format - PLAIN TEXT style per operational memory standards.
    NO fancy HTML blocks. Clean professional format.
    """
    
    subject = f"{business_name} - Technical Health Audit of {website}"
    
    # Plain text body - bfisher format
    body = f"""Dear {contact_name},

I've been researching local {industry} providers in {city}, and I conducted a technical health audit of {business_name}'s digital presence.

To save you time, I have summarized the three critical areas currently impacting your customer acquisition and search ranking:

AREA                STATUS              THE RISK TO THE FIRM
--------------------------------------------------------------------------------
Mobile Speed        🔴 CRITICAL         The site takes {load_time} seconds to load. Emergency customers searching on phones will abandon your site before it even appears.

Security & Trust    🟡 WARNING          The site lacks HTTPS encryption. This flags your business as "Not Secure" to customers and causes Google to penalize your ranking.

Lead Capture        🟢 OPPORTUNITY      With {page_weight} of data to download, potential leads are "timing out" on mobile networks before they can call you.

The Solution: I specialize in helping {city} {industry} businesses bridge these gaps. I would like to offer you a 14-day "AI Intake" trial. We can deploy an intelligent phone system that answers emergency calls 24/7, qualifies leads, and schedules appointments—ensuring you never miss a job.

My Local Guarantee: Because I am a {city} resident, I would like to fix your Mobile Performance for free this week. I will optimize your load time to get you back into Google's "Green" zone and ensure you are the first firm customers see when they need help fast.

I have attached your full Performance Report and a 1-page Executive Summary. I'll follow up with your office in an hour to see if you have any questions.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152
www.aiserviceco.com
"""
    
    # Create mixed multipart for attachments
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = "Daniel Coffman <owner@aiserviceco.com>"
    msg['To'] = to_email
    
    # Attach plain text body
    msg.attach(MIMEText(body, 'plain'))
    
    # Add attachments
    if attachment_paths:
        for filepath in attachment_paths:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                with open(filepath, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)
                    print(f"   📎 Attached: {filename}")
            else:
                print(f"   ⚠️ File not found: {filepath}")
    
    return msg


def send_email(service, message) -> dict:
    """Send email via Gmail API"""
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        sent = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f"   ✅ Email sent! Message ID: {sent['id']}")
        return {"success": True, "message_id": sent['id']}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def main():
    """
    Test send - DO NOT USE FOR PRODUCTION
    Production emails must go through board review first!
    """
    print("=" * 60)
    print("GMAIL API EMAIL SENDER - bfisher Format")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 60)
    
    # Get Gmail service
    print("\n[1] Authenticating with Gmail API...")
    service = get_gmail_service()
    print("   ✅ Authenticated!")
    
    # Example test email (to Dan for testing only)
    print("\n[2] Creating test email in bfisher format...")
    email = create_bfisher_email(
        to_email="nearmiss1193@gmail.com",  # Test recipient ONLY
        business_name="Test Company",
        contact_name="Mr. Test",
        website="testcompany.com",
        industry="HVAC",
        city="Lakeland",
        load_time="13.7",
        page_weight="6.4MB",
        attachment_paths=[]  # Add paths to PDF audit report here
    )
    
    # Send test
    print("\n[3] Sending test email...")
    result = send_email(service, email)
    
    if result["success"]:
        print("\n✅ Test email sent to nearmiss1193@gmail.com")
        print("   Check your inbox!")
    else:
        print(f"\n❌ Failed: {result['error']}")


if __name__ == "__main__":
    main()
