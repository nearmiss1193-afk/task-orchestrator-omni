
import os
import resend
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
if not RESEND_API_KEY:
    print("❌ No Resend API Key found.")
    exit(1)

resend.api_key = RESEND_API_KEY

def send_report():
    print("📧 Sending Mission Report...")
    
    html_content = """
    <h1>🛡️ Protocol Omega: Save Complete</h1>
    <p><strong>System Status:</strong> <span style="color:green;">AUTONOMOUS (24/7)</span></p>
    
    <h3>Recent Actions</h3>
    <ul>
        <li><strong>Backup:</strong> Securely Zipped & Pushed to GitHub (nearmiss1193/orchestrator-omni)</li>
        <li><strong>Campaign:</strong> "Follow the Sun" Strategy Active</li>
        <li><strong>Leads:</strong> Midwest Zone Activated (35 New Leads)</li>
        <li><strong>Feature:</strong> Human Handoff Integrated (+1 352-936-8152)</li>
    </ul>

    <h3>Next Autonomous Steps</h3>
    <p>System will continue hunting and dialing across US timezones (skipping Texas).</p>
    
    <p><em>- Sovereign Executive System</em></p>
    """

    try:
        r = resend.Emails.send({
            "from": "Empire Unified <onboarding@resend.dev>",
            "to": "nearmiss1193@gmail.com",
            "subject": "🛡️ Protocol Omega: Mission Report & Backup Status",
            "html": html_content
        })
        print(f"✅ Email Sent (ID: {r['id']})")
    except Exception as e:
        print(f"❌ Email Failed: {e}")

if __name__ == "__main__":
    send_report()
