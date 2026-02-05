#!/usr/bin/env python3
"""
Send bfisher-format emails with:
1. Traffic Light Table (HTML)
2. PDF Audit Report
3. PageSpeed Screenshot

Uses real PageSpeed data from captured results.
"""
import os
import sys
import json
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Gmail API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

PAGESPEED_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\pagespeed_results"
OUTPUT_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\email_attachments"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Prospects with PageSpeed mappings
PROSPECTS = [
    {"company": "Vanguard Plumbing & Air", "email": "preview@test.com", "contact": "Team", "website": "vanguardplumbingair.com", "niche": "Plumbing/HVAC", "ps_file": "Vanguard_Plumbing_and_Air_pagespeed.json"},
    {"company": "Five Points Roofing", "email": "preview@test.com", "contact": "Team", "website": "fivepointsroofingfl.com", "niche": "Roofing", "ps_file": "Five_Points_Roofing_pagespeed.json"},
    {"company": "Original Pro Plumbing", "email": "preview@test.com", "contact": "Team", "website": "originalplumber.com", "niche": "Plumbing", "ps_file": "Original_Pro_Plumbing_pagespeed.json"},
    {"company": "Hunter Plumbing Inc", "email": "preview@test.com", "contact": "Team", "website": "hunterplumbinginc.com", "niche": "Plumbing", "ps_file": "Hunter_Plumbing_Inc_pagespeed.json"},
    {"company": "Andress Electric", "email": "preview@test.com", "contact": "Team", "website": "andresselectric.com", "niche": "Electrical", "ps_file": "Andress_Electric_pagespeed.json"},
    {"company": "Leaf Electric", "email": "preview@test.com", "contact": "Team", "website": "leafelectricfl.com", "niche": "Electrical", "ps_file": "Leaf_Electric_pagespeed.json"},
    {"company": "Curry Plumbing", "email": "preview@test.com", "contact": "Team", "website": "curryplumbing.com", "niche": "Plumbing", "ps_file": "Curry_Plumbing_pagespeed.json"},
    {"company": "B&W Plumbing LLC", "email": "preview@test.com", "contact": "Team", "website": "bandwplumbing.com", "niche": "Plumbing", "ps_file": "BandW_Plumbing_LLC_pagespeed.json"},
    {"company": "Trimm Roofing", "email": "preview@test.com", "contact": "Team", "website": "trimmroofing.com", "niche": "Roofing", "ps_file": "Trimm_Roofing_pagespeed.json"},
    {"company": "Lakeland Air Conditioning", "email": "preview@test.com", "contact": "Team", "website": "thelakelandac.com", "niche": "HVAC", "ps_file": "Lakeland_AC_pagespeed.json"},
]

def load_pagespeed_data(ps_file):
    """Load PageSpeed results from JSON file."""
    filepath = os.path.join(PAGESPEED_DIR, ps_file)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

def get_traffic_light_status(score):
    """Return status emoji and color based on score."""
    if score is None or score == 'ERR':
        return "🟡", "WARNING", "#FFD700"
    if score < 50:
        return "🔴", "CRITICAL", "#FF0000"
    elif score < 80:
        return "🟡", "WARNING", "#FFD700"
    else:
        return "🟢", "GOOD", "#00FF00"

def create_pdf_audit(prospect, ps_data, output_path):
    """Create a professional PDF audit report."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Header style
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=18, textColor=HexColor('#1a365d'), spaceAfter=12)
    subheader_style = ParagraphStyle('SubHeader', parent=styles['Heading2'], fontSize=14, textColor=HexColor('#2c5282'), spaceAfter=8)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, spaceAfter=6)
    
    # Title
    story.append(Paragraph(f"<b>Digital Performance Audit</b>", header_style))
    story.append(Paragraph(f"<b>{prospect['company']}</b>", subheader_style))
    story.append(Paragraph(f"Website: {prospect['website']}", body_style))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 20))
    
    # Get scores
    mobile_score = ps_data.get('mobile', {}).get('score', 'N/A') if ps_data else 'N/A'
    mobile_lcp = ps_data.get('mobile', {}).get('lcp', 'N/A') if ps_data else 'N/A'
    desktop_score = ps_data.get('desktop', {}).get('score', 'N/A') if ps_data else 'N/A'
    
    mobile_emoji, mobile_status, _ = get_traffic_light_status(mobile_score if mobile_score != 'N/A' else None)
    
    # Executive Summary
    story.append(Paragraph("<b>EXECUTIVE SUMMARY</b>", subheader_style))
    if mobile_score != 'N/A' and mobile_score < 50:
        summary = f"Your website's mobile performance is critically below industry standards. With a score of {mobile_score}/100 and a load time of {mobile_lcp}, you are losing potential customers who abandon slow-loading sites. This audit identifies key issues and provides actionable solutions."
    elif mobile_score != 'N/A' and mobile_score < 80:
        summary = f"Your website shows moderate performance with a mobile score of {mobile_score}/100. While functional, there are optimization opportunities that could improve customer acquisition. The {mobile_lcp} load time is above the recommended threshold."
    else:
        summary = f"Your website performs well with a mobile score of {mobile_score}/100. Minor optimizations could further enhance the user experience and improve conversion rates."
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 20))
    
    # Critical Findings - Traffic Light Table
    story.append(Paragraph("<b>CRITICAL FINDINGS</b>", subheader_style))
    
    table_data = [
        ['AREA', 'STATUS', 'IMPACT'],
        ['Mobile Speed', f'{mobile_emoji} {mobile_status}', f'Score: {mobile_score}/100, LCP: {mobile_lcp}'],
        ['Desktop Speed', f'{get_traffic_light_status(desktop_score if desktop_score != "N/A" else None)[0]} {get_traffic_light_status(desktop_score if desktop_score != "N/A" else None)[1]}', f'Score: {desktop_score}/100'],
        ['Lead Capture', '🟢 OPPORTUNITY', 'AI-powered intake can capture 24/7 leads'],
    ]
    
    t = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f7fafc')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Proposed Solutions
    story.append(Paragraph("<b>PROPOSED SOLUTIONS</b>", subheader_style))
    solutions = [
        "1. <b>Mobile Optimization</b> - Compress images, minify CSS/JS, implement lazy loading",
        "2. <b>AI Intake System</b> - Deploy 24/7 AI phone answering to capture leads while you work",
        "3. <b>Performance Monitoring</b> - Weekly performance reports to track improvements",
    ]
    for sol in solutions:
        story.append(Paragraph(sol, body_style))
    story.append(Spacer(1, 20))
    
    # CTA
    story.append(Paragraph("<b>NEXT STEPS</b>", subheader_style))
    story.append(Paragraph("I'll follow up with your office to discuss these findings. A 14-day trial of our AI Intake system is available to immediately capture leads you may be missing.", body_style))
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph("—" * 50, body_style))
    story.append(Paragraph("<b>Daniel Coffman</b>", body_style))
    story.append(Paragraph("Owner, AI Service Co", body_style))
    story.append(Paragraph("352-936-8152 | www.aiserviceco.com", body_style))
    
    doc.build(story)
    return output_path

def create_html_email(prospect, ps_data):
    """Create HTML email body with traffic light table."""
    mobile_score = ps_data.get('mobile', {}).get('score', 'N/A') if ps_data else 'N/A'
    mobile_lcp = ps_data.get('mobile', {}).get('lcp', 'N/A') if ps_data else 'N/A'
    desktop_score = ps_data.get('desktop', {}).get('score', 'N/A') if ps_data else 'N/A'
    
    mobile_emoji, mobile_status, mobile_color = get_traffic_light_status(mobile_score if mobile_score != 'N/A' else None)
    desktop_emoji, desktop_status, desktop_color = get_traffic_light_status(desktop_score if desktop_score != 'N/A' else None)
    
    html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">

<p><b>[PREVIEW - Original Recipient: {prospect.get('original_email', prospect['email'])}]</b></p>

<p>Dear {prospect['contact']},</p>

<p>I've been researching local {prospect['niche']} providers in Lakeland, and I conducted a technical health audit of {prospect['company']}'s digital presence.</p>

<p>To save you time, I have summarized the critical areas currently impacting your customer acquisition:</p>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px; margin: 15px 0;">
    <tr style="background-color: #1a365d; color: white;">
        <th style="text-align: left;">AREA</th>
        <th style="text-align: left;">STATUS</th>
        <th style="text-align: left;">THE RISK TO THE FIRM</th>
    </tr>
    <tr>
        <td><b>Mobile Speed</b></td>
        <td style="background-color: {mobile_color}20;"><b>{mobile_emoji} {mobile_status}</b></td>
        <td>Score: {mobile_score}/100. Site takes {mobile_lcp} to load. Emergency customers searching on phones will abandon before it appears.</td>
    </tr>
    <tr>
        <td><b>Desktop Speed</b></td>
        <td style="background-color: {desktop_color}20;"><b>{desktop_emoji} {desktop_status}</b></td>
        <td>Score: {desktop_score}/100. Desktop performance affects Google rankings and professional impression.</td>
    </tr>
    <tr>
        <td><b>Lead Capture</b></td>
        <td style="background-color: #00FF0020;"><b>🟢 OPPORTUNITY</b></td>
        <td>AI-powered 24/7 intake system can capture after-hours emergency calls.</td>
    </tr>
</table>

<p><b>The Solution:</b> I specialize in helping Lakeland {prospect['niche']} businesses optimize their digital presence. I'd like to offer you a <b>14-day "AI Intake" trial</b> - deploy an intelligent phone system that answers emergency calls 24/7, qualifies leads, and schedules appointments.</p>

<p><b>My Local Guarantee:</b> As a Lakeland resident, I'll optimize your mobile performance for free this week to get you into Google's "Green" zone.</p>

<p>I've attached your full Performance Report. I'll follow up with your office shortly to see if you have any questions.</p>

<p>Best regards,</p>

<p><b>Daniel Coffman</b><br>
Owner, AI Service Co<br>
352-936-8152<br>
www.aiserviceco.com</p>

<hr style="margin-top: 30px;">
<p style="font-size: 11px; color: #666;">
AI Service Co, Lakeland, FL 33801<br>
If you'd prefer not to receive emails about website performance, reply with "REMOVE" and I'll update my list immediately.
</p>

</body>
</html>
"""
    return html

def get_gmail_service():
    """Get authenticated Gmail API service."""
    creds = None
    token_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_token.json"
    creds_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_credentials.json"
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def send_email(service, to_email, subject, html_body, attachments):
    """Send email with attachments via Gmail API."""
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = "Daniel Coffman <owner@aiserviceco.com>"
    msg['To'] = to_email
    
    # Attach HTML body
    msg.attach(MIMEText(html_body, 'html'))
    
    # Attach files
    for filepath in attachments:
        if os.path.exists(filepath):
            filename = os.path.basename(filepath)
            with open(filepath, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)
                print(f"   📎 Attached: {filename}")
    
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return result.get('id')

def main():
    print("=" * 70)
    print("BFISHER EMAIL SENDER - With Real PageSpeed Data")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get Gmail service
    print("\n📧 Connecting to Gmail API...")
    service = get_gmail_service()
    print("   ✅ Connected")
    
    sent = 0
    failed = 0
    
    for i, prospect in enumerate(PROSPECTS, 1):
        print(f"\n[{i}/10] Processing: {prospect['company']}...")
        
        # Load PageSpeed data
        ps_data = load_pagespeed_data(prospect['ps_file'])
        if ps_data:
            mobile_score = ps_data.get('mobile', {}).get('score', 'N/A')
            print(f"   📊 Mobile Score: {mobile_score}/100")
        else:
            print(f"   ⚠️ No PageSpeed data found")
        
        # Create PDF audit
        pdf_name = prospect['company'].replace(' ', '_').replace('&', 'and')
        pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_name}_Digital_Audit_Feb_2026.pdf")
        print(f"   📄 Generating PDF audit...")
        create_pdf_audit(prospect, ps_data, pdf_path)
        
        # Store original email for preview header
        prospect['original_email'] = prospect['email']
        
        # Create HTML email
        html_body = create_html_email(prospect, ps_data)
        
        # Send to preview address
        preview_email = "nearmiss1193@gmail.com"
        subject = f"[PREVIEW] {prospect['company']} - Technical Health Audit of {prospect['website']}"
        
        try:
            print(f"   📧 Sending email...")
            msg_id = send_email(service, preview_email, subject, html_body, [pdf_path])
            print(f"   ✅ Sent! Message ID: {msg_id}")
            sent += 1
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: {sent} sent, {failed} failed")
    print("=" * 70)

if __name__ == "__main__":
    main()
