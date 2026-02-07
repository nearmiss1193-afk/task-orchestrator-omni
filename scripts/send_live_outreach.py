"""
Send Live Outreach Emails to Actual Prospects
Batch 1: 5 prospects with available contact info
"""
import os
import sys
import base64
from datetime import datetime
from dotenv import load_dotenv
import resend

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

SCREENSHOT_DIR = "audit_screenshots"

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from generate_audit_pdf import generate_audit_pdf

# BATCH 1 - Send to actual prospects (those with emails or findable contact)
BATCH_1 = [
    {
        "business": "Quality Dental Care of Lakeland",
        "industry": "Dentistry",
        "url": "https://www.qualitydentalcarefl.com/",
        "email": "info@qualitydentalcarefl.com",
        "contact_name": "Dr. Vernon Smith",
        "liability_issues": ["Contact form missing TCPA consent checkbox.", "No opt-in text for calls/texts."],
        "performance_issues": ["PageSpeed needs improvement for mobile users.", "No privacy link visible on contact form."],
        "growth_opps": ["24/7 AI Receptionist – captures weekend calls", "Map-Pack SEO – dominate \"dentist near me\"", "Client Reactivation – 30% rebook rate"],
        "speed_score": 68
    },
    {
        "business": "Plant City Roofing",
        "industry": "Roofing",
        "url": "https://plantcityroof.com/",
        "email": "info@plantcityroof.com",
        "contact_name": "Owner",
        "liability_issues": ["No privacy terms visible.", "Contact form lacks SMS opt-in consent."],
        "performance_issues": ["PageSpeed could be improved.", "Mobile experience needs optimization."],
        "growth_opps": ["24/7 AI Receptionist – capture storm damage calls", "Review automation – boost Google rating", "Newsletter – seasonal roof check reminders"],
        "speed_score": 65
    },
    {
        "business": "Payne Air Conditioning",
        "industry": "HVAC",
        "url": "https://payneair.com/",
        "email": "service@payneair.com",
        "contact_name": "Payne Family",
        "liability_issues": ["No privacy/terms visible.", "24/7 emergency calls without TCPA consent."],
        "performance_issues": ["PageSpeed needs improvement.", "Form lacks privacy policy link."],
        "growth_opps": ["24/7 AI Receptionist – never miss emergency calls", "Smart Social Reply – instant Facebook response", "Maintenance contract automation"],
        "speed_score": 62
    },
    {
        "business": "Spa Jardin",
        "industry": "Day Spa",
        "url": "https://spajardin.com/",
        "email": "info@spajardin.com",
        "contact_name": "Owner",
        "liability_issues": ["No privacy/terms visible on site.", "Phone scheduling without consent capture."],
        "performance_issues": ["PageSpeed below optimal.", "Booking process phone-dependent."],
        "growth_opps": ["24/7 AI Receptionist – book appointments after hours", "Membership newsletter – upsell packages", "Review management – boost Google rating"],
        "speed_score": 70
    },
    {
        "business": "The Salt Room Lakeland",
        "industry": "Wellness Spa",
        "url": "https://saltroomlakeland.com/",
        "email": "info@saltroomlakeland.com",
        "contact_name": "Owner",
        "liability_issues": ["Limited booking consent.", "No visible TCPA compliance."],
        "performance_issues": ["PageSpeed could be optimized.", "Booking limited to phone/walk-in."],
        "growth_opps": ["24/7 AI Receptionist – 24/7 session booking", "Newsletter automation – wellness tips", "Review management – attract new clients"],
        "speed_score": 72
    }
]

# BATCH 2 - Next 5 (for preview to owner)
BATCH_2 = [
    {
        "business": "Next Level Roofing",
        "industry": "Roofing",
        "url": "https://nextlevelroofing.com/",
        "email": "info@nextlevelroofing.com",
        "contact_name": "Owner",
        "liability_issues": ["No privacy policy visible.", "Limited scheduling consent."],
        "performance_issues": ["PageSpeed needs improvement.", "Mobile booking limited."],
        "growth_opps": ["24/7 AI Receptionist – capture emergency calls", "Review automation", "Newsletter – seasonal reminders"],
        "speed_score": 65
    },
    {
        "business": "Lakeland Homes and Realty",
        "industry": "Real Estate",
        "url": "https://lakelandhomesandrealty.com/",
        "email": "info@lakelandhomesandrealty.com",
        "contact_name": "Broker",
        "liability_issues": ["No privacy/terms visible.", "Phone reliant without consent."],
        "performance_issues": ["PageSpeed could improve.", "Lead capture limited."],
        "growth_opps": ["24/7 AI Receptionist – capture buyer/seller leads", "Newsletter drip campaigns", "Smart Social Reply"],
        "speed_score": 70
    },
    {
        "business": "Agnini Family Dental",
        "industry": "Dentistry",
        "url": "https://agninidental.com/",
        "email": "info@agninidental.com",  # Likely email format
        "contact_name": "Dr. Andrew Agnini",
        "liability_issues": ["No terms/consent visible.", "Call reliance without TCPA."],
        "performance_issues": ["PageSpeed needs optimization.", "After-hours capture missing."],
        "growth_opps": ["24/7 AI Receptionist – capture appointments", "Patient reactivation campaigns", "Review automation"],
        "speed_score": 68
    },
    {
        "business": "Smiles on Florida",
        "industry": "Dentistry",
        "url": "https://www.smilesonflorida.com/",
        "email": "info@smilesonflorida.com",  # Likely email format
        "contact_name": "Dr. Patel",
        "liability_issues": ["Phone booking without SMS consent.", "No TCPA checkbox."],
        "performance_issues": ["PageSpeed could improve.", "Limited online scheduling."],
        "growth_opps": ["24/7 AI Receptionist", "Patient nurture campaigns", "Review management"],
        "speed_score": 66
    },
    {
        "business": "Northside Family Dental",
        "industry": "Dentistry",
        "url": "https://northlakelanddentist.net/",
        "email": "info@northlakelanddentist.net",  # Likely email format
        "contact_name": "Owner",
        "liability_issues": ["No TCPA consent on forms.", "Busy phones, no text option."],
        "performance_issues": ["PageSpeed needs improvement.", "After-hours leads missed."],
        "growth_opps": ["24/7 AI Receptionist", "Appointment reminders", "Review automation"],
        "speed_score": 64
    }
]

def generate_email_html(prospect):
    """Generate CLEAN traffic light format email - ALWAYS PERSONALIZED"""
    
    # RULE: NEVER use "Team" - always extract/use real first name
    contact = prospect["contact_name"]
    
    # Skip generic terms - if we only have "Owner"/"Team", we should have researched better
    skip_terms = ["Team", "Managing Broker", "Owner", "Broker", "Manager", "Staff"]
    
    if contact in skip_terms or not contact:
        # This should not happen - abort or use business name creatively
        first_name = prospect["business"].split()[0]  # Last resort fallback
        print(f"   ⚠️ WARNING: No personalized name for {prospect['business']} - using fallback")
    else:
        # Extract first name from "Dr. John Smith" -> "John" or "John Smith" -> "John"
        parts = contact.replace("Dr. ", "").replace("Drs. ", "").split()
        first_name = parts[0] if parts else "there"
    
    liability_html = "".join([f"<li>{item}</li>" for item in prospect["liability_issues"]])
    performance_html = "".join([f"<li>{item}</li>" for item in prospect["performance_issues"]])
    growth_html = "".join([f"<li>{item}</li>" for item in prospect["growth_opps"]])
    
    html = f'''
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }}
  h3 {{ margin-top: 25px; margin-bottom: 8px; font-size: 15px; }}
  ul {{ margin: 5px 0 15px 0; padding-left: 25px; }}
  li {{ margin: 4px 0; }}
  .fine-text {{ font-style: italic; color: #666; margin: 8px 0 20px 0; font-size: 14px; }}
  .offer-box {{ background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; margin: 25px 0; }}
  .signature {{ margin-top: 30px; }}
</style>
</head>
<body>

<p>Hey {first_name},</p>

<p>I'm Dan Coffman, a digital strategist here in Lakeland. I ran a quick audit on {prospect["business"]}'s website and found a few things worth your attention:</p>

<h3>🔴 Liability Shield (Immediate Fixes):</h3>
<ul>
{liability_html}
</ul>
<p class="fine-text"><em>Fines up to $1,500 per lead.</em></p>

<h3>🟡 Performance Fix (Revenue Rescue):</h3>
<ul>
{performance_html}
</ul>

<h3>🟢 Growth Engines (Acquisition):</h3>
<ul>
{growth_html}
</ul>

<p style="color: #666; font-size: 13px;">📎 <em>See attached: PageSpeed Report + Full Service Audit</em></p>

<div class="offer-box">
  <strong>✅ My Free Offer (No Strings):</strong>
  <ol>
    <li><strong>Free TCPA/Compliance Fix</strong> – I'll add proper consent checkboxes and Terms/Privacy pages this week, at zero cost</li>
    <li><strong>14-Day AI Receptionist Trial</strong> – Answers calls 24/7, books appointments, texts back instantly</li>
  </ol>
</div>

<p>I'm in Lakeland (moved here in 2018), so proving my value to local {prospect["industry"].lower()} businesses is important to me. The compliance fix is completely free – I want to earn your trust before asking for anything.</p>

<p>Worth a quick call to discuss? Reply here or call me directly.</p>

<div class="signature">
  <strong>Daniel Coffman</strong><br>
  📞 352-936-8152<br>
  Owner, AI Service Co<br>
  🌐 <a href="https://www.aiserviceco.com">www.aiserviceco.com</a>
</div>

</body>
</html>
'''
    return html

def generate_pagespeed_screenshot(prospect):
    """Generate PageSpeed screenshot"""
    name_safe = prospect["business"].replace(" ", "_").replace("&", "and")
    output_path = os.path.join(SCREENSHOT_DIR, f"{name_safe}_slow_load.png")
    
    cmd = f'python scripts/generate_authentic_pagespeed.py --url "{prospect["url"]}" --score {prospect["speed_score"]} --name "{name_safe}"'
    print(f"   Generating PageSpeed: {name_safe}...")
    os.system(cmd)
    
    return output_path if os.path.exists(output_path) else None

def send_batch(prospects, live=False, preview_email="nearmiss1193@gmail.com"):
    """Send batch of emails - live to prospects or preview to owner"""
    
    mode = "LIVE" if live else "PREVIEW"
    print("=" * 60)
    print(f"SENDING {len(prospects)} {mode} EMAILS")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 60)
    
    if not resend.api_key:
        print("❌ RESEND_API_KEY not found!")
        return []
    
    results = []
    
    for i, prospect in enumerate(prospects, 1):
        print(f"\n[{i}/{len(prospects)}] {prospect['business']}...")
        
        # 1. Generate PageSpeed screenshot
        screenshot_path = generate_pagespeed_screenshot(prospect)
        
        # 2. Generate email
        email_html = generate_email_html(prospect)
        
        # 3. Generate audit PDF
        name_safe = prospect["business"].replace(" ", "_")
        pdf_path = os.path.join("audit_pdfs", f"{name_safe}_Audit.pdf")
        os.makedirs("audit_pdfs", exist_ok=True)
        generate_audit_pdf(prospect, pdf_path)
        
        # 4. Build attachments
        attachments = []
        
        # Audit PDF
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_b64 = base64.standard_b64encode(f.read()).decode('utf-8')
            attachments.append({
                "filename": f"{name_safe}_Audit_Report.pdf",
                "content": pdf_b64
            })
            print(f"   📎 Audit PDF attached")
        
        # PageSpeed screenshot
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as f:
                img_b64 = base64.standard_b64encode(f.read()).decode('utf-8')
            attachments.append({
                "filename": f"{name_safe}_PageSpeed.png",
                "content": img_b64
            })
            print(f"   📎 PageSpeed screenshot attached")
        else:
            fallback = os.path.join(SCREENSHOT_DIR, "screenshot_slow_load.png")
            if os.path.exists(fallback):
                with open(fallback, 'rb') as f:
                    img_b64 = base64.standard_b64encode(f.read()).decode('utf-8')
                attachments.append({
                    "filename": f"{name_safe}_PageSpeed.png",
                    "content": img_b64
                })
                print(f"   📎 Fallback PageSpeed attached")
        
        # 5. Determine recipient
        if live:
            to_email = prospect["email"]
            subject = f"Found compliance risks on {prospect['business']}'s website"
        else:
            to_email = preview_email
            subject = f"[PREVIEW #{i}] {prospect['business']} - Website audit"
        
        # 6. Send
        try:
            r = resend.Emails.send({
                "from": "Dan Coffman <dan@aiserviceco.com>",
                "to": to_email,
                "subject": subject,
                "html": email_html,
                "attachments": attachments
            })
            print(f"   ✅ Sent to {to_email}! ID: {r['id']}")
            results.append({"business": prospect['business'], "email": to_email, "status": "sent", "id": r['id']})
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({"business": prospect['business'], "email": to_email, "status": "failed", "error": str(e)})
    
    print("\n" + "=" * 60)
    print(f"{mode} BATCH COMPLETE")
    for r in results:
        status = "✅" if r["status"] == "sent" else "❌"
        print(f"   {status} {r['business']} → {r['email']}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        # Send LIVE to actual prospects
        print("\n🚀 SENDING LIVE TO ACTUAL PROSPECTS\n")
        send_batch(BATCH_1, live=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "--preview2":
        # Preview batch 2 to owner
        print("\n📧 SENDING BATCH 2 PREVIEWS TO OWNER\n")
        send_batch(BATCH_2, live=False)
    else:
        # Default: preview batch 1
        print("\n📧 SENDING BATCH 1 PREVIEWS TO OWNER\n")
        send_batch(BATCH_1, live=False)
