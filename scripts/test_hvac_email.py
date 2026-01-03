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

def send_hvac_test():
    print("🚀 HVAC CAMPAIGN: Initializing Test Sequence...")
    
    # 1. Generate Content
    engine = AdAttackEngine()
    # Mocking 'Tardiness' scenario which is mapped in the engine
    ads = engine.scan_and_attack("Competitor X") 
    target_ad = ads[0] # Tardiness ad

    # 2. Format Email
    subject = f"HVAC TEST: {target_ad['headline']}"
    html_body = f"""
    <h1>🚀 V50.0 Campaign Test: HVAC Vertical</h1>
    <p><strong>Target:</strong> Homeowners with 15+ year old AC units.</p>
    <hr>
    <h2>PREVIEW: AD COPY</h2>
    <p><strong>Headline:</strong> {target_ad['headline']}</p>
    <p><strong>Body:</strong> {target_ad['body']}</p>
    <p><strong>Visual Prompt (Cinematic):</strong><br>
    <em>{target_ad['video_prompt']}</em></p>
    <hr>
    <p><em>This email confirms the 'Deep Research' + 'Expert Prompt' pipeline is active for HVAC.</em></p>
    """
    
    print(f"   📧 Sending to: {OWNER_EMAIL}...")
    
    try:
        r = resend.Emails.send({
            "from": "alert@aiserviceco.com",
            "to": OWNER_EMAIL,
            "subject": subject,
            "html": html_body
        })
        print(f"   ✅ Email Sent! ID: {r['id']}")
    except Exception as e:
        print(f"   ❌ Email Failed: {e}")

if __name__ == "__main__":
    send_hvac_test()
