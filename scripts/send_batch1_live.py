#!/usr/bin/env python3
"""Send Batch 1 live emails to real recipients."""
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Batch 1 prospects from email_drafts_batch1_revised.md
BATCH1 = [
    {"company": "Vanguard Plumbing & Air", "email": "info@vanguardplumbingair.com", "subject": "Vanguard Plumbing - Website Speed Report"},
    {"company": "Five Points Roofing", "email": "fivepointsroofingfl@gmail.com", "subject": "Five Points Roofing - Website Performance Opportunity"},
    {"company": "The Original Pro Plumbing", "email": "info@originalplumber.com", "subject": "Original Pro Plumbing - Website Speed Report"},
    {"company": "Hunter Plumbing Inc", "email": "info@hunterplumbinginc.com", "subject": "Hunter Plumbing - Website Performance Report"},
    {"company": "Andress Electric", "email": "contact@andresselectric.com", "subject": "Andress Electric - Website Performance Report"},
    {"company": "Leaf Electric", "email": "info@leafelectricfl.com", "subject": "Leaf Electric - Website Performance Opportunity"},
    {"company": "Curry Plumbing", "email": "service@curryplumbing.com", "subject": "Curry Plumbing - Website Performance Report"},
    {"company": "B&W Plumbing LLC", "email": "info@bandwplumbing.com", "subject": "B&W Plumbing - Website Speed Report"},
    {"company": "Trimm Roofing", "email": "contact@trimmroofing.com", "subject": "Trimm Roofing - Website Performance Report"},
    {"company": "Lakeland Air Conditioning", "email": "service@thelakelandac.com", "subject": "Lakeland AC - Website Performance Report"},
]

# PageSpeed data from actual tests
PS_DATA = {
    "Vanguard Plumbing & Air": {"mobile": 30, "lcp": "18.3s", "desktop": 68},
    "Five Points Roofing": {"mobile": 84, "lcp": "3.4s", "desktop": 97},
    "The Original Pro Plumbing": {"mobile": 66, "lcp": "5.7s", "desktop": 99},
    "Hunter Plumbing Inc": {"mobile": 80, "lcp": "4.1s", "desktop": 97},
    "Andress Electric": {"mobile": 53, "lcp": "13.8s", "desktop": 99},
    "Leaf Electric": {"mobile": 83, "lcp": "3.2s", "desktop": 87},
    "Curry Plumbing": {"mobile": 70, "lcp": "9.0s", "desktop": 52},
    "B&W Plumbing LLC": {"mobile": 64, "lcp": "5.5s", "desktop": 90},
    "Trimm Roofing": {"mobile": 52, "lcp": "17.5s", "desktop": 76},
    "Lakeland Air Conditioning": {"mobile": 63, "lcp": "6.8s", "desktop": 88},
}

def get_status(score):
    if score < 50: return "🔴 CRITICAL", "#FF0000"
    elif score < 80: return "🟡 WARNING", "#FFD700"
    return "🟢 GOOD", "#00FF00"

def create_email_html(p):
    ps = PS_DATA.get(p['company'], {"mobile": 50, "lcp": "5s", "desktop": 75})
    m_status, m_color = get_status(ps['mobile'])
    d_status, d_color = get_status(ps['desktop'])
    
    html = f"""
<html><body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">

<p>Dear {p['company']} Team,</p>

<p>I recently conducted a technical audit of your website and wanted to share what I found.</p>

<p><b>PERFORMANCE SUMMARY:</b></p>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; max-width: 600px;">
    <tr style="background-color: #1a365d; color: white;">
        <th>Area</th><th>Status</th><th>Impact</th>
    </tr>
    <tr>
        <td>Mobile Speed</td>
        <td style="background-color: {m_color}30;"><b>{m_status}</b></td>
        <td>Score: {ps['mobile']}/100. Load time: {ps['lcp']}. Emergency customers may leave before page appears.</td>
    </tr>
    <tr>
        <td>Desktop Speed</td>
        <td style="background-color: {d_color}30;"><b>{d_status}</b></td>
        <td>Score: {ps['desktop']}/100.</td>
    </tr>
    <tr>
        <td>Lead Capture</td>
        <td style="background-color: #00FF0030;"><b>🟢 OPPORTUNITY</b></td>
        <td>AI-powered 24/7 intake can capture after-hours emergency calls.</td>
    </tr>
</table>

<p><b>The Solution:</b></p>
<p>I help Lakeland-area service businesses capture more emergency calls with 24/7 AI phone systems.</p>

<ol>
<li><b>Free Performance Consultation</b> - I'll identify what's causing slow load times at no cost.</li>
<li><b>14-Day AI Intake Trial</b> - AI answers calls when your team is busy, qualifies leads, schedules appointments.</li>
</ol>

<p><b>Next Step:</b> Reply to this email or call me at 352-936-8152.</p>

<p>Best regards,</p>
<p><b>Daniel Coffman</b><br>Owner, AI Service Co<br>352-936-8152<br>www.aiserviceco.com</p>

<hr><p style="font-size: 11px; color: #666;">AI Service Co, Lakeland, FL 33801<br>Reply "REMOVE" to unsubscribe.</p>
</body></html>
"""
    return html

def get_gmail():
    creds = None
    token_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_token.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('gmail', 'v1', credentials=creds)

def send(service, to, subject, html, attachments=None):
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = "Daniel Coffman <owner@aiserviceco.com>"
    msg['To'] = to
    msg.attach(MIMEText(html, 'html'))
    
    if attachments:
        for fp in attachments:
            if os.path.exists(fp):
                with open(fp, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(fp)}"')
                    msg.attach(part)
    
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return service.users().messages().send(userId='me', body={'raw': raw}).execute().get('id')

if __name__ == "__main__":
    print("=" * 60)
    print("BATCH 1 LIVE EMAIL SENDER")
    print("=" * 60)
    
    service = get_gmail()
    print("✅ Gmail connected\n")
    
    PDF_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\email_attachments"
    sent, failed = 0, 0
    
    for i, p in enumerate(BATCH1, 1):
        print(f"[{i}/10] {p['company']}")
        print(f"   To: {p['email']}")
        
        html = create_email_html(p)
        
        # Find PDF
        pdf_name = p['company'].replace(' ', '_').replace('&', 'and')
        pdf = os.path.join(PDF_DIR, f"{pdf_name}_Digital_Audit_Feb_2026.pdf")
        attachments = [pdf] if os.path.exists(pdf) else []
        
        try:
            msg_id = send(service, p['email'], p['subject'], html, attachments)
            print(f"   ✅ SENT! ID: {msg_id}")
            sent += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: {sent} sent, {failed} failed")
    print("=" * 60)
