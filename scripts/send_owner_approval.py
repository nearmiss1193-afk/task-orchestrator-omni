"""
Send Email Drafts to Dan for Owner Approval
Per /system_ops protocol: Owner approval requires EMAIL to Dan
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = "owner@aiserviceco.com"
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

DAN_EMAIL = "nearmiss1193@gmail.com"

def send_approval_request():
    """Send consolidated email with all 6 drafts for owner approval"""
    
    subject = "APPROVAL REQUESTED: 6 Email Drafts (Board Approved 4/4)"
    
    html_body = """
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <h1 style="color: #2563eb;">📧 Email Drafts Ready for Your Approval</h1>
        
        <div style="background: #dcfce7; border: 1px solid #16a34a; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <strong>✅ BOARD VOTE: 4/4 UNANIMOUS</strong><br>
            Claude ✅ | Grok ✅ | Gemini ✅ | ChatGPT ✅
        </div>
        
        <h2>Your Decision</h2>
        <p>Reply to this email with:</p>
        <ul>
            <li><strong>APPROVE</strong> - Send all 6 emails</li>
            <li><strong>REVISE</strong> - Make changes (specify what)</li>
            <li><strong>REJECT</strong> - Do not send</li>
        </ul>
        
        <hr>
        
        <h2>Email 1: Tony Agnello - Lakeland AC</h2>
        <p><strong>To:</strong> info@thelakelandac.com</p>
        <div style="background: #f5f5f5; padding: 15px; border-left: 3px solid #2563eb; margin: 10px 0;">
            <p>Dear Tony,</p>
            <p>I just completed a technical audit of Lakeland Air Conditioning's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: ATTENTION NEEDED</strong> - 63/100 score, 4.2 second load time. This slow loading speed is likely causing you to lose potential customers who are searching for AC repair on their phones, especially during peak heatwaves.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 85/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152 to schedule your free consultation.</p>
        </div>
        
        <hr>
        
        <h2>Email 2: Nathane Trimm - Trimm Roofing</h2>
        <p><strong>To:</strong> support@trimmroofing.com</p>
        <div style="background: #f5f5f5; padding: 15px; border-left: 3px solid #2563eb; margin: 10px 0;">
            <p>Dear Nathane,</p>
            <p>I just completed a technical audit of Trimm Roofing's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: CRITICAL</strong> - 52/100 score, 5.1 second load time. With almost half of all roofing searches happening on mobile devices, a score this low means you are losing significant leads to competitors. Customers looking for urgent roof repairs after a storm are unlikely to wait.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 88/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152 to schedule your free consultation.</p>
        </div>
        
        <hr>
        
        <h2>Email 3: Chris Shills - Curry Plumbing</h2>
        <p><strong>To:</strong> chrisshills@curryplumbing.com</p>
        <div style="background: #f5f5f5; padding: 15px; border-left: 3px solid #2563eb; margin: 10px 0;">
            <p>Dear Chris,</p>
            <p>I just completed a technical audit of Curry Plumbing's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: WARNING</strong> - 70/100 score, 3.8 second load time. While 70 isn't terrible, it's still slow enough to cause a noticeable drop in conversions. Customers searching for a plumber on their phone often need help immediately.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 92/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152 to schedule your free consultation.</p>
        </div>
        
        <hr>
        
        <h2>Email 4: Marshall Andress - Andress Electric</h2>
        <p><strong>To:</strong> info@andresselectric.com</p>
        <div style="background: #f5f5f5; padding: 15px; border-left: 3px solid #2563eb; margin: 10px 0;">
            <p>Dear Marshall,</p>
            <p>I just completed a technical audit of Andress Electric's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: CRITICAL</strong> - 53/100 score, 4.6 second load time. In the electrical service industry, speed is crucial. A mobile speed score of 53 means you are likely losing out on customers seeking immediate electrical assistance.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 87/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152 to schedule your free consultation.</p>
        </div>
        
        <hr>
        
        <h2>Email 5: Bill Lerch - Hunter Plumbing</h2>
        <p><strong>To:</strong> hunterplumbing@hunterplumbinginc.com</p>
        <div style="background: #f5f5f5; padding: 15px; border-left: 3px solid #2563eb; margin: 10px 0;">
            <p>Dear Bill,</p>
            <p>I just completed a technical audit of Hunter Plumbing's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: GOOD</strong> - 80/100 score, 2.9 second load time. Your website performs well!</li>
                <li><strong>Desktop Performance: GOOD</strong> - 94/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - The main opportunity is capturing after-hours emergency calls when your team isn't available.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152 to schedule your free consultation.</p>
        </div>
        
        <hr>
        
        <h2>Email 6: David Smith - Original Pro Plumbing</h2>
        <p><strong>To:</strong> proplumbing1@originalplumber.com</p>
        <div style="background: #f5f5f5; padding: 15px; border-left: 3px solid #2563eb; margin: 10px 0;">
            <p>Dear David,</p>
            <p>I just completed a technical audit of Original Pro Plumbing's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: WARNING</strong> - 66/100 score, 3.7 second load time. Customers searching for quick home repair solutions expect immediate responsiveness. Your site speed is not as competitive as it could be.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 89/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152 to schedule your free consultation.</p>
        </div>
        
        <hr>
        
        <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <strong>⏳ Waiting for your approval</strong><br>
            Reply: APPROVE / REVISE / REJECT
        </div>
        
        <p style="color: #666; margin-top: 30px;">
            <em>Sent via Antigravity automation per /system_ops protocol</em><br>
            <em>Board approval: 4/4 unanimous (Feb 5, 2026)</em>
        </p>
    </body>
    </html>
    """
    
    if not GMAIL_APP_PASSWORD:
        print("❌ ERROR: GMAIL_APP_PASSWORD not set!")
        print("   Need to set GMAIL_APP_PASSWORD in .env")
        return False
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"Daniel Coffman <{GMAIL_USER}>"
    msg['To'] = DAN_EMAIL
    
    plain_text = "Please view this email in HTML format to see the full drafts."
    msg.attach(MIMEText(plain_text, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        print(f"Connecting to Gmail SMTP...")
        print(f"From: {GMAIL_USER}")
        print(f"To: {DAN_EMAIL}")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, DAN_EMAIL, msg.as_string())
        server.quit()
        print(f"✅ Approval request email sent to {DAN_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SENDING APPROVAL REQUEST TO DAN")
    print("=" * 60)
    success = send_approval_request()
    if success:
        print("\n✅ Email sent! Waiting for Dan's reply:")
        print("   APPROVE / REVISE / REJECT")
    else:
        print("\n❌ Failed to send. Check error above.")
"""
Send Email Drafts to Dan for Owner Approval
Per /system_ops protocol: Owner approval requires EMAIL to Dan
"""
