"""
Send prospecting emails via Gmail SMTP
Uses owner@aiserviceco.com

REQUIRES: Gmail App Password (not regular password)
To get: Google Account → Security → 2-Step Verification → App Passwords
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Gmail Configuration
GMAIL_USER = "owner@aiserviceco.com"
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")  # Need to set this!

# Test recipient (Dan)
TEST_EMAIL = "nearmiss1193@gmail.com"

def create_traffic_light_email(business_name: str, contact_name: str, industry: str, score: int) -> tuple:
    """Create Traffic Light format email"""
    
    # Determine status based on score
    if score < 50:
        status_color = "🔴 CRITICAL"
        status_text = f"Your site scored **{score}/100** on Google PageSpeed - a significant penalty affecting your visibility."
    elif score < 75:
        status_color = "🟡 WARNING"
        status_text = f"Your site scored **{score}/100** - in the 'needs improvement' zone."
    else:
        status_color = "🟢 GOOD"
        status_text = f"Your site scored **{score}/100** - performing well!"
    
    subject = f"{business_name} - Your Website Performance Audit is Ready"
    
    # HTML Email Body
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <p>Dear {contact_name},</p>
        
        <p>I am a local digital strategist here in Lakeland, and I've conducted a brief health audit of {business_name}'s online presence.</p>
        
        <h3 style="color: {'#d9534f' if score < 50 else '#f0ad4e' if score < 75 else '#5cb85c'}">Your PageSpeed Score: {score}/100</h3>
        
        <h3>Traffic Light Summary</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f5f5f5;">
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">AREA</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">STATUS</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">RISK</th>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Search Visibility</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{status_color}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{status_text}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Legal Compliance</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">🟡 WARNING</td>
                <td style="padding: 10px; border: 1px solid #ddd;">Missing Privacy Policy page. Florida law requires this for data collection.</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Lead Efficiency</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">⚪ OPPORTUNITY</td>
                <td style="padding: 10px; border: 1px solid #ddd;">An intelligent intake system could pre-qualify leads 24/7.</td>
            </tr>
        </table>
        
        <h3>What I'm Offering</h3>
        <ol>
            <li><strong>Free PageSpeed Fix</strong> - I'll move your site from {score} → 90+ this week, at no cost</li>
            <li><strong>14-Day Intelligent Intake Trial</strong> - AI assistant that pre-qualifies leads 24/7</li>
        </ol>
        
        <h3>My Local Guarantee</h3>
        <p>Because I am a local Lakeland resident, I want to prove my value before asking for anything. The PageSpeed fix is completely free.</p>
        
        <p>I will follow up with your office in an hour to see if you have any questions.</p>
        
        <p>
            <strong>Daniel Coffman</strong><br>
            📞 352-936-8152<br>
            Owner, AI Service Co<br>
            🌐 <a href="https://www.aiserviceco.com">www.aiserviceco.com</a>
        </p>
    </body>
    </html>
    """
    
    return subject, html_body

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send email via Gmail SMTP"""
    
    if not GMAIL_APP_PASSWORD:
        print("❌ ERROR: GMAIL_APP_PASSWORD not set!")
        print("   To get one:")
        print("   1. Go to: myaccount.google.com/security")
        print("   2. Enable 2-Step Verification if not already")
        print("   3. Go to: myaccount.google.com/apppasswords")
        print("   4. Select 'Mail' and 'Windows Computer'")
        print("   5. Copy the 16-character password")
        print("   6. Add to .env: GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
        return False
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"Daniel Coffman <{GMAIL_USER}>"
    msg['To'] = to_email
    
    # Create plain text version
    plain_text = "Please view this email in HTML format for the full audit report."
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        print(f"   Connecting to Gmail SMTP...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()
        print(f"   ✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print(f"SENDING TEST EMAILS VIA GMAIL SMTP")
    print(f"From: {GMAIL_USER}")
    print(f"To: {TEST_EMAIL}")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 60)
    
    # Create and send test email
    print("\n[1/1] Creating Traffic Light email for Scott's AC...")
    subject, body = create_traffic_light_email(
        business_name="Scott's Air Conditioning",
        contact_name="Craig",
        industry="HVAC",
        score=34
    )
    
    print(f"   Subject: {subject}")
    print(f"   Sending...")
    
    success = send_email(TEST_EMAIL, subject, body)
    
    if success:
        print(f"\n✅ Test email sent to {TEST_EMAIL}")
        print("   Check your inbox!")
    else:
        print(f"\n❌ Failed to send. See error above.")

if __name__ == "__main__":
    main()
