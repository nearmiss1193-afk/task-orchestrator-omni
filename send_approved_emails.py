"""
Send V3 APPROVED Emails to ACTUAL Recipients
APPROVED by Dan at 6:17 PM Feb 5, 2026
"""
import os
import sys
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Add scripts to path
sys.path.insert(0, 'scripts')
from gmail_api_sender import get_gmail_service

def send_to_recipient(service, prospect, pdf_path, html_path):
    """Send email to actual recipient"""
    
    # Read HTML email content
    with open(html_path, 'r', encoding='utf-8') as f:
        html_body = f.read()
    
    # Create message to ACTUAL RECIPIENT
    msg = MIMEMultipart('mixed')
    msg['Subject'] = f"Quick question about {prospect['website']}"
    msg['From'] = f"Daniel Coffman <owner@aiserviceco.com>"
    msg['To'] = prospect['email']  # ACTUAL RECIPIENT
    
    # Attach HTML body
    msg.attach(MIMEText(html_body, 'html'))
    
    # Attach PDF
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'pdf')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = f"{prospect['business'].replace(' ', '_')}_Performance_Audit.pdf"
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
            print(f"   📎 Attached: {filename}")
    else:
        print(f"   ❌ PDF not found: {pdf_path}")
        return False
    
    # Send via Gmail API
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    try:
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        print(f"   ✅ SENT to {prospect['email']}! ID: {result['id']}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 70)
    print("🚀 SENDING APPROVED V3 EMAILS TO ACTUAL RECIPIENTS")
    print(f"   Approved by Dan at 6:17 PM | {datetime.now().strftime('%I:%M %p')}")
    print("=" * 70)
    
    # Load email packages
    with open("email_packages_v3.json", 'r') as f:
        packages = json.load(f)
    
    # Get Gmail service
    print("\nConnecting to Gmail API...")
    service = get_gmail_service()
    print("✅ Connected!\n")
    
    sent_count = 0
    results = []
    
    for i, pkg in enumerate(packages, 1):
        prospect = pkg['prospect']
        pdf_path = pkg['pdf']
        html_path = pkg['html']
        
        print(f"[{i}/{len(packages)}] {prospect['business']} → {prospect['email']}")
        
        if send_to_recipient(service, prospect, pdf_path, html_path):
            sent_count += 1
            results.append({
                "business": prospect['business'],
                "email": prospect['email'],
                "status": "SENT",
                "timestamp": datetime.now().isoformat()
            })
        else:
            results.append({
                "business": prospect['business'],
                "email": prospect['email'],
                "status": "FAILED",
                "timestamp": datetime.now().isoformat()
            })
    
    # Log results
    with open("sent_emails_log.json", 'w') as f:
        json.dump({
            "batch": "V3",
            "approved_at": "2026-02-05T18:17:04",
            "sent_at": datetime.now().isoformat(),
            "total": len(packages),
            "succeeded": sent_count,
            "emails": results
        }, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"🎉 COMPLETE! Sent {sent_count}/{len(packages)} emails!")
    print("=" * 70)
    
    for r in results:
        status_emoji = "✅" if r['status'] == "SENT" else "❌"
        print(f"   {status_emoji} {r['business']} → {r['email']}")
    
    print("\n📋 Results logged to: sent_emails_log.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
