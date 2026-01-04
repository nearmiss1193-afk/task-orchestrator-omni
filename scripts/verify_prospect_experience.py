
import os
import sys
from dotenv import load_dotenv
import resend

# Allow imports
sys.path.append(os.getcwd())

from modules.growth.ad_attack_engine import AdAttackEngine

load_dotenv()
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "nearmiss1193@gmail.com")

if not RESEND_API_KEY:
    print("❌ Critical: RESEND_API_KEY missing from environment.")
    sys.exit(1)

resend.api_key = RESEND_API_KEY

def simulate_prospect_experience():
    print("🚀 SOVEREIGN VERIFICATION: B2B Prospect Experience (Mike Davison - Owner)...")
    
    # 1. Config
    prospect_name = "Mike Davison"
    company_name = "Iceberg HVAC Services"
    prospect_pain = "Tardiness" 
    
    # 2. Generate Content (The Brain)
    engine = AdAttackEngine()
    ads = engine.scan_and_attack(company_name) # Passing actual company name
    target_ad = next((ad for ad in ads if ad['target_pain'] == prospect_pain), ads[0])

    print(f"   👤 Prospect: {prospect_name} (Owner of {company_name})")
    print(f"   🎯 Pain: {prospect_pain}")
    
    # 3. Construct the EXACT Touchpoints (B2B)
    
    # --- SMS (Cold Drip) ---
    sms_body = f"Hey Mike, saw a bad review on Iceberg's Google profile about techs showing up late. I have an AI dispatcher that fixes this instantly. Want a demo? - [Your Name]"
    
    # --- EMAIL (Solution Pitch) ---
    email_subject = f"Fixing the 'Tardiness' reviews for {company_name}"
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; padding: 20px;">
        <h2 style="color: #0275d8;">{target_ad['headline']}</h2>
        <p>Hi {prospect_name.split()[0]},</p>
        <p>I was analyzing {company_name}'s recent feedback and noticed a trend: <strong>{target_ad['target_pain']}</strong>.</p>
        
        <p><em>"{target_ad['body']}"</em></p>
        
        <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0;">
            <strong>📹 HOW WE FIX IT (Visual Concept):</strong><br>
            <em>{target_ad['video_prompt']}</em>
        </div>

        <p><a href="#" style="background-color: #0275d8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">See the AI Dispatcher in Action</a></p>
        
        <p>Best,<br>
        Empire Growth Team<br>
        <em>"We automate your agency."</em></p>
    </div>
    
    <hr style="margin-top: 40px;">
    <h3>📱 SMS PREVIEW (Sent 2 mins later):</h3>
    <div style="background-color: #e9ecef; padding: 15px; border-radius: 10px; font-family: monospace;">
        {sms_body}
    </div>
    """
    
    # 4. SEND (The Action)
    print(f"   📧 Sending B2B Simulation to: {OWNER_EMAIL}...")
    
    try:
        r = resend.Emails.send({
            "from": "alert@aiserviceco.com",
            "to": OWNER_EMAIL,
            "subject": f"B2B PROSPECT SIMULATION: {prospect_name}",
            "html": email_html,
            "text": f"PROSPECT: {prospect_name} (Owner)\nPAIN: {prospect_pain}\n\nEMAIL BODY:\n{target_ad['body']}\n\nVIDEO PROMPT: {target_ad['video_prompt']}\n\nSMS BODY:\n{sms_body}"
        })
        print(f"   ✅ B2B Simulation Sent! ID: {r['id']}")
    except Exception as e:
        print(f"   ❌ Simulation Failed: {e}")

if __name__ == "__main__":
    simulate_prospect_experience()
