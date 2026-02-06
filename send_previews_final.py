"""
Send Individual Preview Emails with PDF Attachments to Dan
Per email_standards.md - Each email exactly as customer will see it
"""
import os
import sys
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Add scripts to path
sys.path.insert(0, 'scripts')
from gmail_api_sender import get_gmail_service

OWNER_EMAIL = "nearmiss1193@gmail.com"

def send_preview(service, prospect, pagespeed, pdf_path, html_path):
    """Send individual preview email with PDF attachment"""
    
    # Read HTML email content
    with open(html_path, 'r', encoding='utf-8') as f:
        html_body = f.read()
    
    # Create message
    msg = MIMEMultipart('mixed')
    msg['Subject'] = f"[PREVIEW] {prospect['business']} - Technical Health Audit"
    msg['From'] = f"Daniel Coffman <owner@aiserviceco.com>"
    msg['To'] = OWNER_EMAIL
    
    # Add preview header
    score = pagespeed.get('performance_score', 'N/A')
    preview_note = f"""
--- PREVIEW MODE ---
This email will be sent TO: {prospect['email']}
PageSpeed Score: {score}/100
Business: {prospect['business']}
Contact: {prospect['name']}
--- REVIEW & APPROVE ---

"""
    
    # Attach HTML body
    msg.attach(MIMEText(html_body, 'html'))
    
    # Attach PDF
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'pdf')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(pdf_path)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
            print(f"   📎 Attached: {filename}")
    else:
        print(f"   ⚠️ PDF not found: {pdf_path}")
    
    # Send via Gmail API
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    try:
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        print(f"   ✅ Sent! Message ID: {result['id']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 70)
    print("SENDING INDIVIDUAL PREVIEW EMAILS WITH ATTACHMENTS")
    print("=" * 70)
    
    # Load email packages
    with open("email_packages_final.json", 'r') as f:
        packages = json.load(f)
    
    # Get Gmail service
    print("\nConnecting to Gmail API...")
    service = get_gmail_service()
    print("✅ Connected!\n")
    
    sent_count = 0
    for i, pkg in enumerate(packages, 1):
        prospect = pkg['prospect']
        pagespeed = pkg['pagespeed']
        pdf_path = pkg['pdf']
        html_path = pkg['html']
        
        print(f"[{i}/{len(packages)}] {prospect['business']} ({prospect['name']})")
        if send_preview(service, prospect, pagespeed, pdf_path, html_path):
            sent_count += 1
    
    print("\n" + "=" * 70)
    print(f"COMPLETE! Sent {sent_count}/{len(packages)} preview emails")
    print("=" * 70)
    print("\n📧 Check your inbox for individual previews with PDF attachments")
    print("📋 Each email shows exactly how customer will see it")


if __name__ == "__main__":
    main()
