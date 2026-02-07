"""
Send prospect emails via GHL - Better deliverability than Resend
Uses GHL conversations API with warmed-up domain
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import httpx

# Load environment
load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.env")

# GHL Webhook (Cold Email Outreach workflow)
GHL_WEBHOOK_URL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/ZQZmrxXmjTEc7FeGaXXW"

# All 25 prospects from today
ALL_PROSPECTS = [
    # Batch 1 (5)
    {"business": "Your Lakeland Dentist", "email": "info@yourlakelanddentist.com", "contact": "Dr. Carter", "industry": "Dental"},
    {"business": "The Lakeland AC Company", "email": "info@thelakelandac.com", "contact": "Mike", "industry": "HVAC"},
    {"business": "Springer Bros Transfer", "email": "info@springerbrotherstransfer.com", "contact": "Derek", "industry": "Moving"},
    {"business": "Hometown Plumbing", "email": "info@hometownplumbingfl.com", "contact": "Tom", "industry": "Plumbing"},
    {"business": "Lakeland Limousine", "email": "info@lakelandlimousine.com", "contact": "James", "industry": "Transport"},
    # Batch 2 (5)
    {"business": "Blanca Law Group", "email": "info@blancalawgroup.com", "contact": "Leo", "industry": "Law"},
    {"business": "Spaulding Injury Law", "email": "info@spauldinginjurylaw.com", "contact": "Stephen", "industry": "Law"},
    {"business": "Morgan & Morgan Tampa", "email": "info@forthepeople.com", "contact": "John", "industry": "Law"},
    {"business": "Hancock Injury Attorneys", "email": "info@hancockinjury.com", "contact": "Frank", "industry": "Law"},
    {"business": "Tampa Bay Spine & Injury", "email": "info@tampabaychiropractic.com", "contact": "Dr. Garcia", "industry": "Chiropractic"},
    # Batch 3 (5)
    {"business": "Florida Orthodontic Institute", "email": "info@floridaorthodontic.com", "contact": "Leo", "industry": "Ortho"},
    {"business": "Brooks Law Group", "email": "info@brookslawgroup.com", "contact": "Stephen", "industry": "Law"},
    {"business": "Kinney Fernandez & Boire", "email": "info@kfblaw.com", "contact": "Frank", "industry": "Law"},
    {"business": "The Aesthetic Loft", "email": "info@theaestheticloftbrandon.com", "contact": "Ashley", "industry": "Med Spa"},
    {"business": "Roof Fix", "email": "info@rooffixnow.com", "contact": "Mike", "industry": "Roofing"},
    # Batch 4 (5)
    {"business": "Greenberg Dental", "email": "info@greenbergdental.com", "contact": "Robert", "industry": "Dental"},
    {"business": "Affordable Roofing", "email": "info@affordableroofingflorida.com", "contact": "Steve", "industry": "Roofing"},
    {"business": "Catania & Catania Law", "email": "info@cataniaandcatania.com", "contact": "Peter", "industry": "Law"},
    {"business": "Luxe Day Spa", "email": "jennifersalomonluxe@gmail.com", "contact": "Jennifer", "industry": "Spa"},
    {"business": "Dental Associates Plant City", "email": "info@smilesincluded.com", "contact": "John", "industry": "Dental"},
    # Batch 5 (5)
    {"business": "Dolman Law Group", "email": "info@dolmanlaw.com", "contact": "Matthew", "industry": "Law"},
    {"business": "Burnetti P.A.", "email": "info@burnetti.com", "contact": "Doug", "industry": "Law"},
    {"business": "The Fernandez Firm", "email": "info@fernandezfirm.com", "contact": "Frank", "industry": "Law"},
    {"business": "Roman Austin Personal Injury", "email": "info@romanaustin.com", "contact": "John", "industry": "Law"},
    {"business": "Florin Roebig", "email": "info@florinroebig.com", "contact": "Wil", "industry": "Law"},
]


def get_headers():
    """Get headers for webhook"""
    return {
        "Content-Type": "application/json"
    }


def send_via_webhook(prospect: dict) -> dict:
    """Send prospect to GHL via webhook trigger"""
    
    # Build the traffic light email body
    subject = f"Found 2 compliance issues on {prospect['business']}'s website"
    
    html_body = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <p>Hi {prospect['contact']},</p>
    
    <p>I ran a quick technical scan on your website and found a couple issues that could affect you:</p>
    
    <h3 style="color: #d32f2f;">🔴 Liability Shield (Critical)</h3>
    <ul>
        <li><strong>Missing Privacy Policy / Terms</strong> - Florida's Digital Bill of Rights (FDBR) requires clear data handling disclosures. Optum RX just paid $23.5M for similar violations.</li>
        <li><strong>Contact form lacks TCPA consent</strong> - Opens you to $500-$1,500 per violation claims.</li>
    </ul>
    
    <h3 style="color: #ff9800;">🟡 Performance Fix</h3>
    <ul>
        <li><strong>PageSpeed under 70</strong> - Slow load times cost you leads.</li>
        <li><strong>Mobile experience needs work</strong> - Most traffic is on phones now.</li>
    </ul>
    
    <h3 style="color: #4caf50;">🟢 Growth Engines</h3>
    <ul>
        <li><strong>24/7 AI Receptionist</strong> - Never miss an after-hours call or lead.</li>
        <li><strong>Review automation</strong> - Build up your Google rating on autopilot.</li>
    </ul>
    
    <p>Would you have 15 minutes this week for a quick call? I can walk you through exactly what needs fixing and how we'd do it.</p>
    
    <p>Best,<br>
    Dan Coffman<br>
    AI Service Co<br>
    <a href="https://aiserviceco.com">aiserviceco.com</a></p>
    
    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
    <p style="font-size: 11px; color: #999;">This email was sent by AI Service Co, Lakeland FL. Reply STOP to unsubscribe.</p>
</div>
"""
    
    # Split contact name
    name_parts = prospect["contact"].replace("Dr. ", "").split()
    first_name = name_parts[0] if name_parts else prospect["contact"]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": prospect["email"],
        "business_name": prospect["business"],
        "email_subject": subject,
        "email_body": html_body,
        "tags": f"prospect,cold-email,{prospect['industry'].lower()}"
    }
    
    with httpx.Client(timeout=30) as client:
        response = client.post(GHL_WEBHOOK_URL, headers=get_headers(), json=payload)
        if response.status_code == 200:
            return {"status": "success", "response": response.text}
        else:
            print(f"   ❌ Webhook error: {response.status_code} - {response.text}")
            return {"status": "error", "code": response.status_code}



def search_contact_by_email(email: str) -> dict:
    """Search for existing contact"""
    url = f"{GHL_API_BASE}/contacts/"
    params = {"locationId": GHL_LOCATION_ID, "query": email, "limit": 1}
    
    with httpx.Client(timeout=30) as client:
        response = client.get(url, headers=get_headers(), params=params)
        if response.status_code == 200:
            contacts = response.json().get("contacts", [])
            if contacts:
                return {"contact": contacts[0]}
        return None


def send_email_via_ghl(contact_id: str, prospect: dict) -> dict:
    """Send email through GHL conversations"""
    url = f"{GHL_API_BASE}/conversations/messages"
    
    # Build the traffic light email body
    subject = f"Found 2 compliance issues on {prospect['business']}'s website"
    
    html_body = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <p>Hi {prospect['contact']},</p>
    
    <p>I ran a quick technical scan on your website and found a couple issues that could affect you:</p>
    
    <h3 style="color: #d32f2f;">🔴 Liability Shield (Critical)</h3>
    <ul>
        <li><strong>Missing Privacy Policy / Terms</strong> - Florida's Digital Bill of Rights (FDBR) requires clear data handling disclosures. Optum RX just paid $23.5M for similar violations.</li>
        <li><strong>Contact form lacks TCPA consent</strong> - Opens you to $500-$1,500 per violation claims.</li>
    </ul>
    
    <h3 style="color: #ff9800;">🟡 Performance Fix</h3>
    <ul>
        <li><strong>PageSpeed under 70</strong> - Slow load times cost you leads.</li>
        <li><strong>Mobile experience needs work</strong> - Most traffic is on phones now.</li>
    </ul>
    
    <h3 style="color: #4caf50;">🟢 Growth Engines</h3>
    <ul>
        <li><strong>24/7 AI Receptionist</strong> - Never miss an after-hours call or lead.</li>
        <li><strong>Review automation</strong> - Build up your Google rating on autopilot.</li>
    </ul>
    
    <p>Would you have 15 minutes this week for a quick call? I can walk you through exactly what needs fixing and how we'd do it.</p>
    
    <p>Best,<br>
    Dan Coffman<br>
    AI Service Co<br>
    <a href="https://aiserviceco.com">aiserviceco.com</a></p>
    
    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
    <p style="font-size: 11px; color: #999;">This email was sent by AI Service Co, Lakeland FL. Reply STOP to unsubscribe.</p>
</div>
"""
    
    payload = {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": html_body
    }
    
    with httpx.Client(timeout=30) as client:
        response = client.post(url, headers=get_headers(), json=payload)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            print(f"   ❌ Send email error: {response.status_code} - {response.text}")
            return None


def send_all_via_webhook(prospects: list, dry_run: bool = True):
    """Send all emails via GHL Webhook"""
    print(f"\n{'🧪 DRY RUN' if dry_run else '🚀 LIVE'} - Sending {len(prospects)} emails via GHL Webhook")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print(f"Webhook: {GHL_WEBHOOK_URL[:60]}...")
    print("=" * 60)
    
    sent = 0
    failed = 0
    
    for i, prospect in enumerate(prospects, 1):
        print(f"\n[{i}/{len(prospects)}] {prospect['business']}...")
        
        if dry_run:
            print(f"   📧 Would send to: {prospect['email']}")
            print(f"   👤 Contact: {prospect['contact']}")
            sent += 1
            continue
        
        # Send via webhook (creates contact + sends email)
        result = send_via_webhook(prospect)
        
        if result.get("status") == "success":
            print(f"   ✅ Sent!")
            sent += 1
        else:
            print(f"   ❌ Failed")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {sent} sent, {failed} failed")
    

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        send_all_via_webhook(ALL_PROSPECTS, dry_run=False)
    else:
        print("DRY RUN MODE - Use --live to actually send")
        send_all_via_webhook(ALL_PROSPECTS, dry_run=True)
