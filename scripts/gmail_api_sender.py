"""
Send emails via Gmail API with OAuth2
Uses gmail_credentials.json from empire-unified

// turbo-all
"""
import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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

def create_traffic_light_email(business_name: str, contact_name: str, score: int, industry: str, attachment_paths: list = None) -> MIMEMultipart:
    """Create Traffic Light format HTML email with optional attachments"""
    
    # Determine status based on score
    if score < 50:
        status_emoji = "🔴"
        status_text = "CRITICAL"
        status_color = "#dc3545"
    elif score < 75:
        status_emoji = "🟡"
        status_text = "WARNING"
        status_color = "#ffc107"
    else:
        status_emoji = "🟢"
        status_text = "GOOD"
        status_color = "#28a745"
    
    subject = f"{business_name} - Why Competitors May Be Ranking Above You"
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333; }}
        .google-header {{ background: linear-gradient(135deg, #4285F4, #34A853); padding: 15px; text-align: center; border-radius: 8px 8px 0 0; }}
        .google-logo {{ font-size: 28px; font-weight: bold; color: white; letter-spacing: 1px; }}
        .google-logo span.g {{ color: #4285F4; background: white; padding: 2px 8px; border-radius: 4px; }}
        .score-box {{ background: {status_color}; color: white; padding: 25px; text-align: center; border-radius: 0 0 8px 8px; margin-bottom: 20px; }}
        .score-number {{ font-size: 72px; font-weight: bold; line-height: 1; }}
        .score-label {{ font-size: 24px; font-weight: bold; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #f5f5f5; padding: 12px; text-align: left; border: 1px solid #ddd; }}
        td {{ padding: 12px; border: 1px solid #ddd; }}
        .critical {{ color: #dc3545; font-weight: bold; }}
        .warning {{ color: #ffc107; font-weight: bold; }}
        .opportunity {{ color: #6c757d; font-weight: bold; }}
        .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
        .screenshot-box {{ background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 8px; padding: 15px; margin: 20px 0; text-align: center; }}
    </style>
</head>
<body>
    <p>Dear {contact_name},</p>
    
    <p>I've analyzed your site and found why local competitors may be ranking above you in Google search results. Here's a quick look at what I discovered:</p>
    
    <!-- LARGE GOOGLE BRANDING -->
    <div class="google-header">
        <div class="google-logo">
            <span class="g">G</span>OOGLE PageSpeed Insights
        </div>
        <div style="color: white; font-size: 14px; margin-top: 8px;">Official Website Performance Analysis</div>
    </div>
    
    <div class="score-box">
        <div class="score-number">{score}/100</div>
        <div class="score-label">{status_emoji} {status_text}</div>
    </div>
    
    <!-- SCREENSHOT PLACEHOLDER -->
    <div class="screenshot-box">
        <p style="margin: 0; color: #666;">📊 <strong>Your full analysis is attached below</strong></p>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #999;">See the detailed report from Google's official testing tool</p>
    </div>
    
    <h3>📊 Traffic Light Summary</h3>
    
    <table>
        <tr>
            <th>AREA</th>
            <th>STATUS</th>
            <th>WHAT THIS MEANS</th>
        </tr>
        <tr>
            <td><strong>Search Visibility</strong></td>
            <td class="critical">{status_emoji} {status_text}</td>
            <td>Your site scored <strong>{score}/100</strong> on Google PageSpeed. {"This puts you at a disadvantage against competitors with faster sites." if score < 50 else "There's room to improve and outpace competitors."}</td>
        </tr>
        <tr>
            <td><strong>Legal Compliance</strong></td>
            <td class="warning">🟡 WARNING</td>
            <td>Missing Privacy Policy page. Florida law requires this for data collection.</td>
        </tr>
        <tr>
            <td><strong>Lead Efficiency</strong></td>
            <td class="opportunity">⚪ OPPORTUNITY</td>
            <td>An intelligent intake system could pre-qualify leads 24/7 for your {industry} business.</td>
        </tr>
    </table>
    
    <h3>🎁 What I'm Offering (Free)</h3>
    <ol>
        <li><strong>Free Speed Optimization</strong> - I'll significantly improve your PageSpeed score this week, at no cost</li>
        <li><strong>14-Day Intelligent Intake Trial</strong> - AI assistant that pre-qualifies leads 24/7</li>
    </ol>
    
    <h3>🏠 My Local Guarantee</h3>
    <p>I'm a local Lakeland business owner myself. I want to prove my value before asking for anything. The speed optimization is <strong>completely free</strong> - results vary based on your current site setup.</p>
    
    <p><strong>Would you be open to a quick 5-minute call this week?</strong> I can walk you through exactly what I found and how to fix it.</p>
    
    <div class="signature">
        <strong>Daniel Coffman</strong><br>
        📞 352-936-8152<br>
        Owner, AI Service Co<br>
        🌐 <a href="https://www.aiserviceco.com">www.aiserviceco.com</a>
    </div>
</body>
</html>
    """
    
    # Create mixed multipart for attachments
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = "Daniel Coffman <owner@aiserviceco.com>"
    msg['To'] = "nearmiss1193@gmail.com"  # Test recipient
    
    # Create alternative part for HTML/plain text
    msg_alt = MIMEMultipart('alternative')
    
    # Plain text fallback
    plain_text = f"Dear {contact_name},\n\nYour PageSpeed Score: {score}/100 ({status_text})\n\nPlease view this email in HTML format for the full audit report.\n\nDaniel Coffman\n352-936-8152"
    
    msg_alt.attach(MIMEText(plain_text, 'plain'))
    msg_alt.attach(MIMEText(html_body, 'html'))
    msg.attach(msg_alt)
    
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

def send_email(service, message):
    """Send email via Gmail API"""
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        sent = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f"   ✅ Email sent! Message ID: {sent['id']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("GMAIL API EMAIL SENDER (Board-Approved v2)")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 60)
    
    # Get Gmail service
    print("\n[1] Authenticating with Gmail API...")
    service = get_gmail_service()
    print("   ✅ Authenticated!")
    
    # Attachment paths
    screenshot_path = r"C:\Users\nearm\.gemini\antigravity\brain\0b97dae9-c5c0-4924-8d97-793b59319985\pagespeed_sample_red_1770300563709.png"
    
    # Create test email with attachment
    print("\n[2] Creating board-approved email for Scott's AC...")
    email = create_traffic_light_email(
        business_name="Scott's Air Conditioning",
        contact_name="Craig",
        score=34,
        industry="HVAC",
        attachment_paths=[screenshot_path]
    )
    
    # Send email
    print("\n[3] Sending email...")
    success = send_email(service, email)
    
    if success:
        print("\n✅ Board-approved email sent to nearmiss1193@gmail.com")
        print("   Check your inbox!")
    else:
        print("\n❌ Failed to send. See error above.")

if __name__ == "__main__":
    main()
