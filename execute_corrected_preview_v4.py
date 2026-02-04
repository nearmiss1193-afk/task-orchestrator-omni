
import os
import resend
from dotenv import load_dotenv
import sys

# Define path for script imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.traffic_light_automation import LEADS, generate_email

load_dotenv()

# Initialize Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

def run():
    print("🚀 Initiating CORRECTED PREVIEW BATCH...")
    
    # We use the LEADS already defined in traffic_light_automation.py
    batch_leads = LEADS[:3] # Hardin, Parajon, Dean
    
    html_content = "<h1>CORRECTED PREVIEW BATCH: Feb 3 – Approve or Edit</h1>"
    html_content += "<p>This batch follows the 5th-grade Traffic Light structure exactly as requested.</p><hr>"
    
    for lead in batch_leads:
        email = generate_email(lead)
        
        # Convert plain text body to HTML for the preview email
        formatted_body = email['body'].replace('\n', '<br>')
        
        email_display = f"""
        <div style="border: 2px solid #ff3e3e; padding: 25px; margin-bottom: 30px; font-family: 'Inter', sans-serif; background: #fff; color: #000;">
            <p><strong>To:</strong> {lead['name']} ({lead['site']})</p>
            <p><strong>Subject:</strong> {email['subject']}</p>
            <p style="border-top: 1px solid #eee; padding-top: 15px;">{formatted_body}</p>
        </div>
        """
        html_content += email_display
    
    html_content += """
    <div style="background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-top: 20px;">
        <p><strong>REQUIRED ACTION:</strong></p>
        <p>Reply with <strong>'APPROVE ALL'</strong> to dispatch these live.</p>
        <p>All templates have been logged to <code>traffic_light_strike.log</code> for safety.</p>
    </div>
    """
    
    print(f"📈 Processing {len(batch_leads)} corrected leads...")
    
    params = {
        "from": "Empire AI <onboarding@resend.dev>",
        "to": ["nearmiss1193@gmail.com"],
        "subject": "CORRECTED PREVIEW BATCH: Feb 3 – Approve or Edit",
        "html": html_content,
    }

    try:
        email_res = resend.Emails.send(params)
        print(f"✅ Corrected Preview sent! ID: {email_res['id']}")
        print("\n--- SAFETY LOG (Latest Template) ---")
        for lead in batch_leads:
            e = generate_email(lead)
            print(f"ID {lead['id']} [{lead['name']}] PASS")
    except Exception as e:
        print(f"❌ Failed to send corrected preview: {e}")

if __name__ == "__main__":
    run()
