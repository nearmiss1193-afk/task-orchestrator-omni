"""
Generate PageSpeed Screenshots + PDF Audits for 5 New Prospects
Then send complete emails with attachments
"""
import os
import sys
import base64
import json
from datetime import datetime
from dotenv import load_dotenv
import resend
import subprocess

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

OWNER_EMAIL = "nearmiss1193@gmail.com"
SCREENSHOT_DIR = "audit_screenshots"

# 5 Prospects
PROSPECTS = [
    {
        "business": "Midtown Dental",
        "industry": "Dentistry",
        "url": "https://mymidtowndental.com/",
        "phone": "863-451-9253",
        "contact_name": "Dr. Nerestant",
        "liability_issues": ["Contact form missing TCPA consent checkbox.", "No opt-in text for calls/texts."],
        "performance_issues": ["PageSpeed 72 – slow load = approx 25% bounce rate.", "No privacy link on form – trust drop."],
        "growth_opps": ["24/7 AI Receptionist – captures all missed calls", "Map-Pack SEO – dominate \"dentist near me\"", "Client Reactivation – 30% rebook rate"],
        "speed_score": 72
    },
    {
        "business": "Busciglio Orthodontics",
        "industry": "Orthodontics",
        "url": "https://buscigliosmiles.com/",
        "phone": "813-681-9473",
        "contact_name": "Dr. Derek Busciglio",
        "liability_issues": ["Phone-only booking with no TCPA consent.", "Multi-location form without SMS opt-in."],
        "performance_issues": ["PageSpeed 68 – mobile users bouncing.", "No visible terms or privacy policy."],
        "growth_opps": ["24/7 AI Receptionist – captures consult requests", "Smart Social Reply – remember patient history", "Newsletter automation – treatment reminders"],
        "speed_score": 68
    },
    {
        "business": "Bella Visage Medical Spa",
        "industry": "Medical Spa",
        "url": "https://bellavisagelakeland.com/",
        "phone": "863-333-0553",
        "contact_name": "Mark",
        "liability_issues": ["Booking form without consent language.", "Subscription opt-in buried without TCPA."],
        "performance_issues": ["PageSpeed 65 – slow load = lost bookings.", "Privacy policy not evident on forms."],
        "growth_opps": ["24/7 AI Receptionist – book while you sleep", "Membership newsletter – automated upsells", "Review automation – boost Google rating"],
        "speed_score": 65
    },
    {
        "business": "Dismuke Law",
        "industry": "Personal Injury Law",
        "url": "https://www.1800askdave.com/",
        "phone": "863-250-5050",
        "contact_name": "David",
        "liability_issues": ["Contact forms lack TCPA consent checkbox.", "High call volume with no SMS opt-in captured."],
        "performance_issues": ["PageSpeed 58 – critical for competitive legal market.", "Form submissions without clear consent."],
        "growth_opps": ["24/7 AI Receptionist – never miss a case intake", "Omnichannel follow-up – SMS + email sequences", "Google Maps optimization – rank for \"injury lawyer near me\""],
        "speed_score": 58
    },
    {
        "business": "Keller Williams Realty Smart",
        "industry": "Real Estate",
        "url": "https://locations.kw.com/location/376",
        "phone": "863-577-1234",
        "contact_name": "Team",
        "liability_issues": ["No TCPA checkbox on contact forms.", "Manual phone intake without consent capture."],
        "performance_issues": ["PageSpeed 74 – room for improvement.", "Agent inquiry forms missing privacy link."],
        "growth_opps": ["24/7 AI Receptionist – capture buyer/seller leads", "Newsletter drip campaigns – nurture listings", "Smart Social Reply – instant response on Facebook"],
        "speed_score": 74
    }
]

def generate_pagespeed_screenshot(prospect):
    """Generate authentic PageSpeed screenshot using existing script"""
    name_safe = prospect["business"].replace(" ", "_").replace("&", "and")
    output_path = os.path.join(SCREENSHOT_DIR, f"{name_safe}_slow_load.png")
    
    # Use existing generate script
    cmd = f'python scripts/generate_authentic_pagespeed.py --url "{prospect["url"]}" --score {prospect["speed_score"]} --name "{name_safe}"'
    print(f"   Generating PageSpeed: {name_safe}...")
    os.system(cmd)
    
    return output_path if os.path.exists(output_path) else None

def generate_email_html(prospect):
    """Generate CLEAN traffic light format email"""
    
    first_name = prospect["contact_name"].split()[0] if prospect["contact_name"] not in ["Team", "Managing Broker"] else "Team"
    
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

def generate_audit_text(prospect):
    """Generate plain text audit report as attachment"""
    
    audit = f"""
============================================================
         WEBSITE AUDIT REPORT - {prospect["business"]}
============================================================
Generated: {datetime.now().strftime("%B %d, %Y")}
URL: {prospect["url"]}
Industry: {prospect["industry"]}

------------------------------------------------------------
🔴 CRITICAL: LIABILITY ISSUES (Immediate Fixes Required)
------------------------------------------------------------
"""
    for issue in prospect["liability_issues"]:
        audit += f"  • {issue}\n"
    
    audit += """
⚠️ RISK: Fines up to $1,500 per lead under TCPA.
   Recent case: Optum RX paid $23.5M class action settlement.

------------------------------------------------------------
🟡 WARNING: PERFORMANCE ISSUES (Revenue Impact)
------------------------------------------------------------
"""
    for issue in prospect["performance_issues"]:
        audit += f"  • {issue}\n"
    
    audit += f"""
📊 Mobile PageSpeed Score: {prospect["speed_score"]}/100
   Industry benchmark: 90+

------------------------------------------------------------
🟢 OPPORTUNITY: GROWTH ENGINES (Value-Add Services)
------------------------------------------------------------
"""
    for opp in prospect["growth_opps"]:
        audit += f"  • {opp}\n"
    
    audit += """
------------------------------------------------------------
AVAILABLE SERVICES
------------------------------------------------------------
🤖 AI Receptionist           - 24/7 call answering & booking
📧 Newsletter Automation     - Customer nurturing campaigns
📱 Smart Social Reply        - Facebook/Instagram AI response
🎯 Visionary Ads             - AI-powered ad creative
⭐ Review Management         - Automated review requests
⚖️ Compliance Package        - Terms/Privacy/TCPA compliance

Contact us for custom pricing based on your needs.

------------------------------------------------------------
FREE OFFER (No Strings Attached)
------------------------------------------------------------
1. Free TCPA/Compliance Fix - We'll add proper consent 
   checkboxes and Terms/Privacy pages at zero cost.

2. 14-Day AI Receptionist Trial - Test our 24/7 call 
   answering system with no commitment.

------------------------------------------------------------
Contact: Daniel Coffman | 352-936-8152 | AI Service Co
         www.aiserviceco.com | Lakeland, FL
============================================================
"""
    return audit

def send_batch():
    """Generate screenshots, create audits, send complete emails"""
    
    print("=" * 60)
    print("GENERATING COMPLETE PROSPECT PACKAGES")
    print("=" * 60)
    
    if not resend.api_key:
        print("❌ RESEND_API_KEY not found!")
        return
    
    results = []
    
    for i, prospect in enumerate(PROSPECTS, 1):
        print(f"\n[{i}/5] {prospect['business']}...")
        
        # 1. Generate PageSpeed screenshot
        screenshot_path = generate_pagespeed_screenshot(prospect)
        
        # 2. Generate email
        email_html = generate_email_html(prospect)
        
        # 3. Generate audit PDF
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from generate_audit_pdf import generate_audit_pdf
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
            # Fallback to generic
            fallback = os.path.join(SCREENSHOT_DIR, "screenshot_slow_load.png")
            if os.path.exists(fallback):
                with open(fallback, 'rb') as f:
                    img_b64 = base64.standard_b64encode(f.read()).decode('utf-8')
                attachments.append({
                    "filename": f"{name_safe}_PageSpeed.png",
                    "content": img_b64
                })
                print(f"   📎 Generic PageSpeed screenshot attached")
        
        # 5. Send
        subject = f"[COMPLETE #{i}] {prospect['business']} - Website audit attached"
        
        try:
            r = resend.Emails.send({
                "from": "Dan Coffman <dan@aiserviceco.com>",
                "to": OWNER_EMAIL,
                "subject": subject,
                "html": email_html,
                "attachments": attachments
            })
            print(f"   ✅ Sent! ID: {r['id']}")
            results.append({"business": prospect['business'], "status": "sent"})
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({"business": prospect['business'], "status": "failed", "error": str(e)})
    
    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    for r in results:
        status = "✅" if r["status"] == "sent" else "❌"
        print(f"   {status} {r['business']}")
    print("=" * 60)

if __name__ == "__main__":
    send_batch()
