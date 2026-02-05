#!/usr/bin/env python3
"""Send emails to real recipients from database."""
import os
import sys
import json
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from supabase import create_client
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

PAGESPEED_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\pagespeed_results"
OUTPUT_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\email_attachments"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# PageSpeed file mapping
PS_MAPPING = {
    "vanguardplumbingair.com": "Vanguard_Plumbing_and_Air_pagespeed.json",
    "fivepointsroofingfl.com": "Five_Points_Roofing_pagespeed.json",
    "originalplumber.com": "Original_Pro_Plumbing_pagespeed.json",
    "hunterplumbinginc.com": "Hunter_Plumbing_Inc_pagespeed.json",
    "andresselectric.com": "Andress_Electric_pagespeed.json",
    "leafelectricfl.com": "Leaf_Electric_pagespeed.json",
    "curryplumbing.com": "Curry_Plumbing_pagespeed.json",
    "bandwplumbing.com": "BandW_Plumbing_LLC_pagespeed.json",
    "trimmroofing.com": "Trimm_Roofing_pagespeed.json",
    "thelakelandac.com": "Lakeland_AC_pagespeed.json",
}

def get_prospects_from_db():
    """Get real prospects with emails from database."""
    url = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    client = create_client(url, key)
    
    r = client.table('contacts_master').select(
        'id,company_name,full_name,email,website_url,niche,phone'
    ).not_.is_('email','null').not_.eq('email','').in_(
        'status',['new','research_done']
    ).limit(10).execute()
    
    return r.data

def load_pagespeed_data(website):
    """Load PageSpeed results for website."""
    # Normalize website
    website = website.lower().replace('https://','').replace('http://','').replace('www.','').rstrip('/')
    
    ps_file = PS_MAPPING.get(website)
    if ps_file:
        filepath = os.path.join(PAGESPEED_DIR, ps_file)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    return None

def get_traffic_light(score):
    if score is None or score == 'N/A':
        return "🟡", "WARNING", "#FFD700"
    if score < 50:
        return "🔴", "CRITICAL", "#FF0000"
    elif score < 80:
        return "🟡", "WARNING", "#FFD700"
    return "🟢", "GOOD", "#00FF00"

def create_pdf_audit(prospect, ps_data, output_path):
    """Create PDF audit report."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    header = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=18, textColor=HexColor('#1a365d'))
    subheader = ParagraphStyle('SubHeader', parent=styles['Heading2'], fontSize=14, textColor=HexColor('#2c5282'))
    body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, spaceAfter=6)
    
    company = prospect.get('company_name') or 'Your Business'
    website = prospect.get('website_url', 'N/A')
    
    story.append(Paragraph("<b>Digital Performance Audit</b>", header))
    story.append(Paragraph(f"<b>{company}</b>", subheader))
    story.append(Paragraph(f"Website: {website}", body))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", body))
    story.append(Spacer(1, 20))
    
    mobile_score = ps_data.get('mobile', {}).get('score', 'N/A') if ps_data else 'N/A'
    mobile_lcp = ps_data.get('mobile', {}).get('lcp', 'N/A') if ps_data else 'N/A'
    desktop_score = ps_data.get('desktop', {}).get('score', 'N/A') if ps_data else 'N/A'
    
    m_emoji, m_status, _ = get_traffic_light(mobile_score if mobile_score != 'N/A' else None)
    d_emoji, d_status, _ = get_traffic_light(desktop_score if desktop_score != 'N/A' else None)
    
    story.append(Paragraph("<b>EXECUTIVE SUMMARY</b>", subheader))
    if mobile_score != 'N/A' and mobile_score < 50:
        summary = f"Your website's mobile performance is critically below standards. Score: {mobile_score}/100, Load time: {mobile_lcp}. This is costing you customers."
    elif mobile_score != 'N/A' and mobile_score < 80:
        summary = f"Moderate performance with mobile score of {mobile_score}/100. Optimization opportunities exist."
    else:
        summary = f"Good performance with mobile score of {mobile_score}/100. Minor optimizations recommended."
    story.append(Paragraph(summary, body))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>CRITICAL FINDINGS</b>", subheader))
    table_data = [
        ['AREA', 'STATUS', 'IMPACT'],
        ['Mobile Speed', f'{m_emoji} {m_status}', f'Score: {mobile_score}/100, LCP: {mobile_lcp}'],
        ['Desktop Speed', f'{d_emoji} {d_status}', f'Score: {desktop_score}/100'],
        ['Lead Capture', '🟢 OPPORTUNITY', 'AI-powered 24/7 intake available'],
    ]
    t = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#1a365d')),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor('#ffffff')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, HexColor('#e2e8f0')),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>PROPOSED SOLUTIONS</b>", subheader))
    story.append(Paragraph("1. Mobile Optimization - Compress images, optimize code", body))
    story.append(Paragraph("2. AI Intake System - 24/7 phone answering for leads", body))
    story.append(Paragraph("3. Performance Monitoring - Weekly reports", body))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>NEXT STEPS</b>", subheader))
    story.append(Paragraph("I'll follow up to discuss. 14-day AI Intake trial available.", body))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("—" * 40, body))
    story.append(Paragraph("<b>Daniel Coffman</b> | Owner, AI Service Co", body))
    story.append(Paragraph("352-936-8152 | www.aiserviceco.com", body))
    
    doc.build(story)

def create_html_email(prospect, ps_data):
    """Create HTML email with traffic light table."""
    company = prospect.get('company_name') or 'Your Business'
    contact = prospect.get('full_name') or 'Team'
    website = prospect.get('website_url', 'your website')
    niche = prospect.get('niche') or 'service'
    
    mobile_score = ps_data.get('mobile', {}).get('score', 'N/A') if ps_data else 'N/A'
    mobile_lcp = ps_data.get('mobile', {}).get('lcp', 'N/A') if ps_data else 'N/A'
    desktop_score = ps_data.get('desktop', {}).get('score', 'N/A') if ps_data else 'N/A'
    
    m_emoji, m_status, m_color = get_traffic_light(mobile_score if mobile_score != 'N/A' else None)
    d_emoji, d_status, d_color = get_traffic_light(desktop_score if desktop_score != 'N/A' else None)
    
    html = f"""
<html><body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">

<p>Dear {contact},</p>

<p>I've been researching local {niche} providers in Lakeland, and I conducted a technical health audit of {company}'s digital presence.</p>

<p>To save you time, I have summarized the critical areas currently impacting your customer acquisition:</p>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; max-width: 600px; margin: 15px 0;">
    <tr style="background-color: #1a365d; color: white;">
        <th>AREA</th><th>STATUS</th><th>THE RISK TO THE FIRM</th>
    </tr>
    <tr>
        <td><b>Mobile Speed</b></td>
        <td style="background-color: {m_color}20;"><b>{m_emoji} {m_status}</b></td>
        <td>Score: {mobile_score}/100. Site takes {mobile_lcp} to load.</td>
    </tr>
    <tr>
        <td><b>Desktop Speed</b></td>
        <td style="background-color: {d_color}20;"><b>{d_emoji} {d_status}</b></td>
        <td>Score: {desktop_score}/100.</td>
    </tr>
    <tr>
        <td><b>Lead Capture</b></td>
        <td style="background-color: #00FF0020;"><b>🟢 OPPORTUNITY</b></td>
        <td>AI-powered 24/7 intake can capture after-hours calls.</td>
    </tr>
</table>

<p><b>The Solution:</b> I specialize in helping Lakeland {niche} businesses. I'd like to offer you a <b>14-day "AI Intake" trial</b>.</p>

<p><b>My Local Guarantee:</b> As a Lakeland resident, I'll optimize your mobile performance for free this week.</p>

<p>I've attached your full Performance Report. I'll follow up shortly.</p>

<p>Best regards,</p>
<p><b>Daniel Coffman</b><br>Owner, AI Service Co<br>352-936-8152<br>www.aiserviceco.com</p>

<hr><p style="font-size: 11px; color: #666;">AI Service Co, Lakeland, FL 33801<br>Reply "REMOVE" to unsubscribe.</p>

</body></html>
"""
    return html

def get_gmail_service():
    """Get Gmail API service."""
    creds = None
    token_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_token.json"
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    return build('gmail', 'v1', credentials=creds)

def send_email(service, to_email, subject, html_body, attachments):
    """Send email with attachments."""
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = "Daniel Coffman <owner@aiserviceco.com>"
    msg['To'] = to_email
    
    msg.attach(MIMEText(html_body, 'html'))
    
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
    print("LIVE EMAIL SENDER - Batch 1")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n📊 Loading prospects from database...")
    prospects = get_prospects_from_db()
    print(f"   Found {len(prospects)} prospects")
    
    print("\n📧 Connecting to Gmail API...")
    service = get_gmail_service()
    print("   ✅ Connected")
    
    sent, failed = 0, 0
    
    for i, p in enumerate(prospects[:10], 1):
        company = p.get('company_name') or 'Business'
        email = p.get('email')
        website = p.get('website_url', '')
        contact = p.get('full_name') or 'Team'
        
        print(f"\n[{i}/10] {company}")
        print(f"   To: {email}")
        print(f"   Contact: {contact}")
        
        # Load PageSpeed data
        ps_data = load_pagespeed_data(website)
        
        # Create PDF
        pdf_name = company.replace(' ', '_').replace('&', 'and').replace('/', '_')
        pdf_path = os.path.join(OUTPUT_DIR, f"{pdf_name}_Audit.pdf")
        create_pdf_audit(p, ps_data, pdf_path)
        print(f"   📄 PDF created")
        
        # Create email
        html_body = create_html_email(p, ps_data)
        subject = f"{company} - Technical Health Audit"
        
        try:
            msg_id = send_email(service, email, subject, html_body, [pdf_path])
            print(f"   ✅ SENT! ID: {msg_id}")
            sent += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: {sent} sent, {failed} failed")
    print("=" * 70)

if __name__ == "__main__":
    main()
