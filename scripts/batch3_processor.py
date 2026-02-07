
import json
import os
import time
import sys
import subprocess
from datetime import datetime

# Add scripts dir to path to import existing modules
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

# Let's import the specific function if possible, or redefine it for safety.
from pipeline_v4_sender import get_gmail_service
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

PROSPECTS_FILE = "prospects_ready.json"
OUTPUT_DIR = "audit_reports"
SCREENSHOTS_DIR = "audit_screenshots"
RECIPIENT_OVERRIDE = "nearmiss1193@gmail.com"  # Safety


def get_industry_hooks(industry):
    # Industry-specific hooks
    hooks = {
        "HVAC": {
            "seo_term": "AC repair near me",
            "client_term": "homeowners",
            "service_term": "emergency repair",
            "trap_example": "Optum RX"
        },
        "Plumbing": {
            "seo_term": "plumber near me",
            "client_term": "homeowners",
            "service_term": "emergency leak repair",
            "trap_example": "Optum RX"
        },
        "Roofing": {
            "seo_term": "roofer near me",
            "client_term": "homeowners",
            "service_term": "roof inspection",
            "trap_example": "Optum RX"
        },
        "Dental": {
            "seo_term": "dentist near me",
            "client_term": "patients", 
            "service_term": "dental implant",
            "trap_example": "Optum RX"
        },
        "Medical": {
            "seo_term": "doctor near me",
            "client_term": "patients", 
            "service_term": "urgent care connection",
            "trap_example": "Optum RX"
        }
    }
    # Default to HVAC if unknown, or generic
    base = hooks.get(industry, hooks["HVAC"]) 
    # Fallback for mapped "HVAC/Plumbing"
    if "/" in industry:
        base = hooks["HVAC"]
    return base

def build_email_dynamic(facts, prospect):
    industry = prospect.get("industry", "Business")
    hooks = get_industry_hooks(industry)
    
    contact_name = prospect.get("name")
    
    # HARD GATE: Name Must Be Real
    if not contact_name or contact_name.lower() in ["business owner", "owner", "team", "manager"]:
         print(f"❌ CRITICAL: Missing or Generic Name for {prospect['company_name']}. SKIPPING.")
         return "ABORT" # Signal to caller
         
    greeting = f"Dear {contact_name},"

    site_url = facts.get("site_url", prospect["website"])
    site_clean = site_url.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
    
    score = facts.get('page_speed', 0)
    bounce = facts.get('mobile_bounce', '20%')
    
    # HTML Construction
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.5;">
        
        <p>{greeting}</p>
        
        <p>I enjoyed reviewing your local reputation earlier. I am a local digital strategist here in Lakeland, and I've conducted a brief technical health audit of your online presence at <a href="{site_url}">{site_clean}</a>.</p>
        
        <p>To save you time, I have summarized the three critical areas currently impacting your firm's online reputation, search ranking, and liability:</p>
        
        <br>
        
        <p style="font-size: 16px;"><strong>The "It Won't Happen to Me" Trap:</strong></p>
        
        <p><em>{hooks['trap_example']} didn't think these types of compliance issues needed to be fixed either... until they paid out millions in settlements.</em></p>
        
        <p>The mentality that "this isn't important" is exactly what leads to bankruptcy-level fines.</p>
        
        <br>
        
        <p style="font-weight: bold; font-size: 15px; margin-bottom: 5px;">🔴 Liability Shield (Immediate Fixes):</p>
        <ul style="margin-top: 0; margin-bottom: 15px; padding-left: 20px;">
            {"<li>No Terms & Conditions page.</li>" if "terms-conditions" not in facts["footer_links"] else ""}
            {"<li>Contact form missing TCPA consent checkbox.</li>" if not facts["contact_form"]["consent_checkbox"] else ""}
            {"<li>No opt-in text for calls/texts.</li>" if not facts["contact_form"]["tcp_consent_text"] else ""}
        </ul>
        <p style="margin-top: -10px; margin-bottom: 20px; padding-left: 20px; font-style: italic;">Fines up to $1,500 per lead.</p>

        <p style="font-weight: bold; font-size: 15px; margin-bottom: 5px;">🟡 Performance Fix (Revenue Rescue):</p>
        <ul style="margin-top: 0; margin-bottom: 20px; padding-left: 20px;">
            {"<li>PageSpeed " + str(score) + " – slow load = approx " + str(bounce) + " bounce rate.</li>" if score < 90 else ""}
            {"<li>No privacy link on form – trust drop.</li>" if not facts["contact_form"]["privacy_link_near_form"] else ""}
        </ul>
        
        <p style="font-weight: bold; font-size: 15px; margin-bottom: 5px;">🟢 Growth Engines (Acquisition):</p>
        <ul style="margin-top: 0; margin-bottom: 20px; padding-left: 20px;">
            <li>24/7 AI Receptionist – captures all missed calls</li>
            <li>Map-Pack SEO – dominate “{hooks['seo_term']}”</li>
            <li>Client Reactivation – 30% rebook rate</li>
        </ul>
        
        <br>
        
        <p><strong>The Solution:</strong> I specialize in helping local businesses bridge these technical gaps. I would like to offer you a 14-day <strong>"Intelligent Intake"</strong> trial. We can install a digital assistant on your site that "pre-screens" potential {hooks['client_term']} before they ever call your office—ensuring your team only spends time on high-value cases.</p>
        
        <p><strong>My Local Guarantee:</strong> Because I am a local Lakeland resident, I would like to <strong>fix your Search Visibility (Google Failure) for free</strong> this week. This will move your site back into the "Green" zone and allow you to see the quality of my work firsthand with zero risk to the firm.</p>
        
        <p>I have attached the full performance report and an Executive Summary for your review. I will follow up with your office in an hour to see if you have any questions.</p>
        
        <p>Best regards,</p>
        
        <p><strong>Daniel Coffman</strong><br>
        Owner, AI Service Co<br>
        352-936-8152<br>
        <a href="http://www.aiserviceco.com">www.aiserviceco.com</a></p>
        
    </body>
    </html>
    """
    return html_body.strip()

def process_prospect(prospect, index):
    print(f"\nExample {index}/10: Processing {prospect['company_name']}...")
    
    url = prospect['website']
    # If URL is empty, skip
    if not url:
        print("   Skipping (No URL)")
        return

    name = prospect['company_name'].replace(" ", "_").replace("&", "and")
    
    facts_file = os.path.join(OUTPUT_DIR, f"{name}_facts.json")
    
    # 1. SCAN 
    if not os.path.exists(facts_file): 
        scan_cmd = ["python", "scripts/single_scan.py", "--url", url, "--name", name, "--output", facts_file]
        print(f"   Running Scan: {' '.join(scan_cmd)}")
        try:
            subprocess.run(scan_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Scan Failed: {e}")
            return
    
    with open(facts_file, 'r') as f:
        facts = json.load(f)

    # 2. GENERATE PDF (With Dynamic Industry)
    # update single_pdf_gen.py to accept industry argument or we pass it? 
    # For speed, let's keep PDF generic "Strategic Solutions" or update the script next.
    # The current PDF script is somewhat generic ("Locally-Owned Business"). 
    # We should make it dynamic too.
    pdf_path = os.path.join(OUTPUT_DIR, f"{name}_proposal.pdf")
    pdf_cmd = ["python", "scripts/single_pdf_gen.py", "--facts", facts_file, "--output", pdf_path, "--industry", prospect.get("industry", "Business")]
    
    try:
        subprocess.run(pdf_cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ PDF Gen Failed")
        return

    # 3. BUILD EMAIL (Dynamic)
    html_body = build_email_dynamic(facts, prospect)
    if html_body == "ABORT":
        return

    # 4. SEND PREVIEW
    send_preview_email(prospect, facts, html_body, pdf_path, name)

def send_preview_email(prospect, facts, html_body, pdf_path, clean_name):
    try:
        service = get_gmail_service()
        msg = MIMEMultipart('mixed')
        msg['to'] = RECIPIENT_OVERRIDE
        msg['from'] = "AI Service Co V6 <owner@aiserviceco.com>"
        msg['subject'] = f"PREVIEW [{prospect['company_name']}]: Strategic Solutions Proposal"
        
        # Attach HTML
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach PDF
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(part)
            
        # Attach Screenshots (from audit_screenshots/name/...)
        # Logic to find the 3 specific screenshots
        # They should be in "audit_screenshots/{clean_name}/" or similar depending on how scanner saves them.
        # I'll assume standard naming "screenshot_terms_missing.png" etc in a specific dir.
        
        # Scanner should define where screenshots go.
        # Let's assume "audit_screenshots/{clean_name}_terms.png" etc for simplicity in single_scan.py
        
        # Dynamic Screenshot attachment logic based on Facts
        screenshot_map = {
             "terms-conditions": (f"{clean_name}_terms_missing.png", "terms-conditions" not in facts["footer_links"]),
             "consent": (f"{clean_name}_no_consent.png", not facts["contact_form"].get("consent_checkbox", False)),
             "speed": (f"{clean_name}_slow_load.png", facts.get("page_speed", 100) < 90)
        }
        
        screen_dir = os.path.join(SCREENSHOTS_DIR) # Flat dir or subdir? I'll use flat with prefix in scan script.

        for key, (fname, condition) in screenshot_map.items():
            if condition:
                fpath = os.path.join(screen_dir, fname)
                if os.path.exists(fpath):
                     with open(fpath, 'rb') as f:
                        img = MIMEApplication(f.read(), Name=fname)
                     img['Content-Disposition'] = f'attachment; filename="{fname}"'
                     msg.attach(img)
                else:
                    print(f"❌ CRITICAL: Missing Evidence Screenshot: {fname}")
                    print("   ABORTING EMAIL SEND to prevent hallucination.")
                    return # Hard Stop

        # Send
        raw_msg = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
        service.users().messages().send(userId='me', body=raw_msg).execute()
        print(f"✅ Preview Sent for {prospect['company_name']}")

    except Exception as e:
        print(f"❌ Email Failed: {e}")
        import traceback
        traceback.print_exc()

import base64

if __name__ == "__main__":
    if not os.path.exists(PROSPECTS_FILE):
        print("❌ No prospects file.")
        sys.exit(1)
        
    with open(PROSPECTS_FILE, 'r') as f:
        prospects = json.load(f)
        
    print(f"🚀 Launching Batch 3 (Previews) - {len(prospects)} total")
    
    # Run top 10
    for i, p in enumerate(prospects[:10]):
        process_prospect(p, i+1)
        time.sleep(2) # Safety buffer

