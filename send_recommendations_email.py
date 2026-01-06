"""
Send System Recommendations Email
=================================
Runs system check and sends recommendations to owner.
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Run quick verification and collect recommendations
def get_system_status():
    """Check system status and generate recommendations."""
    recommendations = []
    status_report = []
    
    # Check GHL
    ghl_token = os.getenv("GHL_API_TOKEN") or os.getenv("GHL_PRIVATE_KEY")
    if ghl_token:
        status_report.append("✅ GHL API: Connected")
    else:
        status_report.append("❌ GHL API: Missing token")
        recommendations.append("Add GHL_API_TOKEN to .env")
    
    # Check Vapi
    vapi_key = os.getenv("VAPI_PRIVATE_KEY")
    if vapi_key:
        status_report.append("✅ Vapi: Connected")
    else:
        status_report.append("❌ Vapi: Missing key")
        recommendations.append("Add VAPI_PRIVATE_KEY to .env")
    
    # Check Resend
    resend_key = os.getenv("RESEND_API_KEY")
    if resend_key:
        status_report.append("✅ Resend Email: Connected")
    else:
        status_report.append("❌ Resend: Missing key")
        recommendations.append("Add RESEND_API_KEY to .env")
    
    # Check Stripe
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    if stripe_key:
        status_report.append("✅ Stripe: Connected")
    else:
        status_report.append("❌ Stripe: Missing key")
        recommendations.append("Add STRIPE_SECRET_KEY to .env")
    
    # Check Supabase
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if supabase_url and supabase_key:
        status_report.append("✅ Supabase: Connected")
    else:
        status_report.append("❌ Supabase: Missing credentials")
        recommendations.append("Add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to .env")
    
    # Add general recommendations
    recommendations.extend([
        "Consider adding backup API keys for all integrations",
        "Schedule weekly system health checks",
        "Enable Vapi call recording for training data",
        "Set up Stripe webhook monitoring",
        "Create GHL workflow for new client onboarding"
    ])
    
    return status_report, recommendations

def send_recommendations_email():
    """Send system recommendations via email."""
    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        print("❌ RESEND_API_KEY not found")
        return False
    
    status_report, recommendations = get_system_status()
    
    email_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; border-radius: 10px;">
            <h1 style="margin: 0;">🛡️ Empire System Report</h1>
            <p style="color: #aaa; margin-top: 10px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div style="padding: 20px;">
            <h2>📊 System Status</h2>
            <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; font-family: monospace;">
                {'<br>'.join(status_report)}
            </div>
            
            <h2 style="margin-top: 30px;">💡 Recommendations</h2>
            <ul style="line-height: 1.8;">
                {''.join(f'<li>{r}</li>' for r in recommendations)}
            </ul>
            
            <h2 style="margin-top: 30px;">📋 Quick Actions</h2>
            <ul>
                <li><a href="https://www.aiserviceco.com/dashboard.html">Open Dashboard</a></li>
                <li><a href="https://app.gohighlevel.com">Open GHL</a></li>
                <li><a href="https://dashboard.vapi.ai">Open Vapi</a></li>
            </ul>
            
            <p style="margin-top: 30px; color: #666; font-size: 12px;">
                This is an automated system report from Empire Unified.
            </p>
        </div>
    </body>
    </html>
    """
    
    recipients = [
        "owner@aiserviceco.com",
        "nearmiss1193@gmail.com"
    ]
    
    for email in recipients:
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Empire System <system@aiserviceco.com>",
                "to": [email],
                "subject": f"🛡️ Empire System Report - {datetime.now().strftime('%Y-%m-%d')}",
                "html": email_html
            },
            timeout=10
        )
        
        if res.status_code in [200, 201]:
            print(f"✅ Email sent to {email}")
        else:
            print(f"❌ Failed to send to {email}: {res.status_code}")
    
    return True

if __name__ == "__main__":
    print("📧 Sending System Recommendations Email...")
    send_recommendations_email()
    print("\n✅ Done!")
