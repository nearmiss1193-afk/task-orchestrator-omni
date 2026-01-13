"""
TURBO OUTREACH - Direct webhook triggers
Sends emails and SMS immediately via GHL webhooks
"""
import requests
import time
from datetime import datetime

# GHL Webhooks
GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"
GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Test prospects - these will receive outreach
PROSPECTS = [
    {
        "business": "ABC Air Conditioning & Heating",
        "email": "owner@aiserviceco.com",  # Send to owner for verification
        "phone": "+13527585336",
        "city": "Orlando",
        "audit_link": "https://prod.analyzemy.business/#/share/report/test-abc-hvac"
    },
]

def send_email(prospect):
    """Send email via GHL webhook"""
    html_body = f"""
    <p>Hey there,</p>
    
    <p>I just ran a quick audit on <b>{prospect['business']}</b> and found some missed call patterns that are costing you revenue.</p>
    
    <p><b>Your Free Deficiency Report:</b><br>
    <a href="{prospect['audit_link']}">{prospect['audit_link']}</a></p>
    
    <p>The report shows exactly where calls are falling through. Most businesses in {prospect['city']} are losing 20-30 calls per week.</p>
    
    <p>We can fix this with AI that answers 24/7 and books jobs while you sleep. <b>14-Day Free Trial</b> - no credit card.</p>
    
    <p>Best,<br>
    Daniel<br>
    AI Service Co<br>
    (352) 758-5336</p>
    """
    
    payload = {
        "email": prospect['email'],
        "from_name": "Daniel",
        "from_email": "daniel@aiserviceco.com",
        "subject": f"Missed calls at {prospect['business']}?",
        "html_body": html_body,
        "company": prospect['business'],
        "audit_link": prospect['audit_link']
    }
    
    try:
        resp = requests.post(GHL_EMAIL, json=payload, timeout=15)
        print(f"✅ EMAIL sent to {prospect['email']} - Status: {resp.status_code}")
        return True
    except Exception as e:
        print(f"❌ EMAIL failed: {e}")
        return False

def send_sms(prospect):
    """Send SMS via GHL webhook"""
    message = f"Hey! I just ran a free audit on {prospect['business']} - found some missed calls costing you money. Check it out: {prospect['audit_link']} Reply STOP to opt out. - Daniel, AI Service Co"
    
    payload = {
        "phone": prospect['phone'],
        "message": message,
        "company": prospect['business']
    }
    
    try:
        resp = requests.post(GHL_SMS, json=payload, timeout=15)
        print(f"✅ SMS sent to {prospect['phone']} - Status: {resp.status_code}")
        return True
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False

def main():
    print("="*60)
    print("🚀 TURBO OUTREACH - DIRECT WEBHOOK MODE")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    stats = {"emails": 0, "sms": 0}
    
    for prospect in PROSPECTS:
        print(f"\n📧 Processing: {prospect['business']}")
        
        if send_email(prospect):
            stats["emails"] += 1
        
        time.sleep(2)
        
        if send_sms(prospect):
            stats["sms"] += 1
        
        time.sleep(2)
    
    print("\n" + "="*60)
    print(f"RESULTS: Emails: {stats['emails']}, SMS: {stats['sms']}")
    print("="*60)
    
    return stats

if __name__ == "__main__":
    main()
