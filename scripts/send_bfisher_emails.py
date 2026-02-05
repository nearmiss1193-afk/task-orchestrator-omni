#!/usr/bin/env python3
"""
Send bfisher-format emails with:
1. Traffic light table (colored HTML)
2. PDF audit report attachment
3. Proper professional format
"""
import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import red, orange, green, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import tempfile

# Preview destination
PREVIEW_EMAIL = "nearmiss1193@gmail.com"

# Prospect data with REAL test results
PROSPECTS = [
    {
        "company": "Vanguard Plumbing & Air",
        "contact": "Team",
        "email": "info@vanguardplumbingair.com",
        "website": "vanguardplumbingair.com",
        "industry": "HVAC and Plumbing",
        "city": "Lakeland",
        "load_time": "5.1",
        "page_weight": "Unknown",
        "ssl_status": "403 Access Error",
        "mobile_status": "CRITICAL",
        "security_status": "WARNING",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "Five Points Roofing",
        "contact": "Team",
        "email": "fivepointsroofingfl@gmail.com",
        "website": "fivepointsroofingfl.com",
        "industry": "Roofing",
        "city": "Lakeland",
        "load_time": "3.6",
        "page_weight": "Unknown",
        "ssl_status": "Valid",
        "mobile_status": "SLOW",
        "security_status": "GOOD",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "The Original Pro Plumbing",
        "contact": "Team",
        "email": "proplumbing1@originalplumber.com",
        "website": "originalplumber.com",
        "industry": "Plumbing",
        "city": "Lakeland",
        "load_time": "2.1",
        "page_weight": "Unknown",
        "ssl_status": "Valid",
        "mobile_status": "SLOW",
        "security_status": "GOOD",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "Hunter Plumbing Inc",
        "contact": "Team",
        "email": "hunterplumbing@hunterplumbinginc.com",
        "website": "hunterplumbinginc.com",
        "industry": "Plumbing",
        "city": "Winter Haven",
        "load_time": "3.8",
        "page_weight": "Unknown",
        "ssl_status": "Valid",
        "mobile_status": "SLOW",
        "security_status": "GOOD",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "Andress Electric",
        "contact": "Team",
        "email": "info@andresselectric.com",
        "website": "andresselectric.com",
        "industry": "Electrical",
        "city": "Lakeland",
        "load_time": "3.8",
        "page_weight": "Unknown",
        "ssl_status": "Valid",
        "mobile_status": "SLOW",
        "security_status": "GOOD",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "Leaf Electric",
        "contact": "Team",
        "email": "leafelectricinfo@gmail.com",
        "website": "leafelectricfl.com",
        "industry": "Electrical",
        "city": "Lakeland",
        "load_time": "3.6",
        "page_weight": "Unknown",
        "ssl_status": "Valid",
        "mobile_status": "SLOW",
        "security_status": "GOOD",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "Curry Plumbing",
        "contact": "Team",
        "email": "curryco@curryplumbing.com",
        "website": "curryplumbing.com",
        "industry": "Plumbing",
        "city": "Lakeland",
        "load_time": "Unknown",
        "page_weight": "Unknown",
        "ssl_status": "SSL Certificate Error",
        "mobile_status": "WARNING",
        "security_status": "CRITICAL",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "B&W Plumbing LLC",
        "contact": "Team",
        "email": "bwplumbing@yahoo.com",
        "website": "bandwplumbing.com",
        "industry": "Plumbing",
        "city": "Lakeland",
        "load_time": "1.9",
        "page_weight": "Unknown",
        "ssl_status": "403 Error from some locations",
        "mobile_status": "GOOD",
        "security_status": "WARNING",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "Trimm Roofing",
        "contact": "Team",
        "email": "support@trimmroofing.com",
        "website": "trimmroofing.com",
        "industry": "Roofing",
        "city": "Lakeland",
        "load_time": "1.8",
        "page_weight": "Unknown",
        "ssl_status": "403 Error from some locations",
        "mobile_status": "GOOD",
        "security_status": "WARNING",
        "lead_status": "OPPORTUNITY"
    },
    {
        "company": "Lakeland Air Conditioning",
        "contact": "Team",
        "email": "info@thelakelandac.com",
        "website": "thelakelandac.com",
        "industry": "HVAC",
        "city": "Lakeland",
        "load_time": "0.684",
        "page_weight": "Unknown",
        "ssl_status": "Valid",
        "mobile_status": "EXCELLENT",
        "security_status": "GOOD",
        "lead_status": "OPPORTUNITY"
    }
]

def get_status_color(status):
    """Return color for status."""
    if status in ["CRITICAL"]:
        return "red"
    elif status in ["WARNING", "SLOW"]:
        return "orange"
    elif status in ["GOOD", "EXCELLENT", "OPPORTUNITY"]:
        return "green"
    return "gray"

def get_status_emoji(status):
    """Return emoji for status."""
    if status in ["CRITICAL"]:
        return "🔴"
    elif status in ["WARNING", "SLOW"]:
        return "🟡"
    elif status in ["GOOD", "EXCELLENT", "OPPORTUNITY"]:
        return "🟢"
    return "⚪"

def create_pdf_audit(prospect, output_path):
    """Create PDF audit report in bfisher format."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], 
                                  fontSize=18, alignment=1, spaceAfter=20)
    story.append(Paragraph("DIGITAL RISK & PERFORMANCE AUDIT", title_style))
    story.append(Spacer(1, 12))
    
    # Client info
    client_style = ParagraphStyle('Client', parent=styles['Normal'], fontSize=10)
    story.append(Paragraph(f"<b>Client:</b> {prospect['company']} | <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", client_style))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], 
                                   fontSize=12, textColor=colors.red, spaceAfter=10)
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    exec_text = f"""A technical assessment of {prospect['website']} has identified critical performance issues that directly 
impact customer acquisition and search engine visibility. The mobile site's performance score indicates 
issues that are likely causing potential customers to abandon the site before it loads."""
    story.append(Paragraph(exec_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Critical Findings
    story.append(Paragraph("CRITICAL FINDINGS", heading_style))
    
    findings = []
    
    # Mobile Speed finding
    if prospect['mobile_status'] in ['CRITICAL', 'SLOW', 'WARNING']:
        findings.append(f"<b>• Mobile Performance Status: {prospect['mobile_status']} ({prospect['load_time']}s)</b>")
        findings.append(f"")
        findings.append(f"<b>• Primary Issue: Excessive Load Time ({prospect['load_time']} seconds):</b> The Google PageSpeed test matrix shows the main content takes {prospect['load_time']} seconds to appear on mobile devices. Emergency {prospect['industry']} customers searching on their phones will abandon your site before it even appears.")
    
    # Security finding
    if prospect['security_status'] in ['CRITICAL', 'WARNING']:
        findings.append(f"")
        findings.append(f"<b>• Security Risk: {prospect['ssl_status']}:</b> The site may not be using secure HTTPS protocol or has certificate issues, exposing customer data and negatively impacting search rankings.")
    
    for finding in findings:
        story.append(Paragraph(finding, styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Proposed Solutions
    story.append(Paragraph("PROPOSED SOLUTIONS", heading_style))
    
    solutions = [
        f"<b>1. Emergency Performance Recovery:</b> Implement critical optimizations to reduce mobile load time from {prospect['load_time']}s to under 3s. This includes image compression, code minification, and caching strategies.",
        "",
        f"<b>2. HTTPS Security Implementation:</b> Install SSL certificate and migrate site to secure HTTPS protocol to protect customer data and improve search rankings.",
        "",
        f"<b>3. AI-Powered After-Hours Phone System:</b> Deploy intelligent phone answering system to capture emergency calls 24/7, qualify leads, and schedule appointments automatically.",
        "",
        f"<b>4. Mobile-First Website Optimization:</b> Comprehensive mobile performance overhaul to ensure fast loading on all devices and network conditions."
    ]
    
    for solution in solutions:
        story.append(Paragraph(solution, styles['Normal']))
    
    doc.build(story)
    return output_path

def create_bfisher_email(prospect):
    """Create HTML email in bfisher format with traffic light table."""
    
    # Status indicators
    mobile_emoji = get_status_emoji(prospect['mobile_status'])
    security_emoji = get_status_emoji(prospect['security_status'])
    lead_emoji = get_status_emoji(prospect['lead_status'])
    
    # Risk text based on status
    if prospect['mobile_status'] == 'CRITICAL':
        mobile_risk = f"The site takes {prospect['load_time']} seconds to load. Emergency customers searching on phones will abandon your site before it even appears."
    elif prospect['mobile_status'] in ['SLOW', 'WARNING']:
        mobile_risk = f"The site takes {prospect['load_time']} seconds to load. This is above Google's recommended 3-second threshold and may cost you leads."
    else:
        mobile_risk = f"Excellent! The site loads in {prospect['load_time']} seconds. You're ahead of most competitors."
    
    if 'SSL' in prospect['ssl_status'] or 'Error' in prospect['ssl_status']:
        security_risk = f"The site has {prospect['ssl_status']}. This flags your business as \"Not Secure\" to customers and causes Google to penalize your ranking."
    else:
        security_risk = "Your SSL certificate is valid and working. Customers see the secure lock icon."
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #333;">

<p>Dear {prospect['contact']},</p>

<p>I've been researching local {prospect['industry']} providers in {prospect['city']}, and I conducted a technical health audit of {prospect['company']}'s digital presence.</p>

<p>To save you time, I have summarized the three critical areas currently impacting your customer acquisition and search ranking:</p>

<table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
<tr style="background-color: #f5f5f5;">
<td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">AREA</td>
<td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">STATUS</td>
<td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">THE RISK TO THE FIRM</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">Mobile Speed</td>
<td style="padding: 10px; border: 1px solid #ddd;">{mobile_emoji} {prospect['mobile_status']}</td>
<td style="padding: 10px; border: 1px solid #ddd;">{mobile_risk}</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">Security & Trust</td>
<td style="padding: 10px; border: 1px solid #ddd;">{security_emoji} {prospect['security_status']}</td>
<td style="padding: 10px; border: 1px solid #ddd;">{security_risk}</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;">Lead Capture</td>
<td style="padding: 10px; border: 1px solid #ddd;">{lead_emoji} {prospect['lead_status']}</td>
<td style="padding: 10px; border: 1px solid #ddd;">With your current digital presence, potential leads are likely finding competitors first. There's an opportunity to capture more emergency calls.</td>
</tr>
</table>

<p><b>The Solution:</b> I specialize in helping {prospect['city']} {prospect['industry']} businesses bridge these gaps. I would like to offer you a <b>14-day "AI Intake" trial</b>. We can deploy an intelligent phone system that answers emergency calls 24/7, qualifies leads, and schedules appointments—ensuring you never miss a job.</p>

<p><b>My Local Guarantee:</b> Because I am a {prospect['city']} resident, I would like to <b>fix your Mobile Performance for free</b> this week. I will optimize your load time to get you back into Google's "Green" zone and ensure you are the first firm customers see when they need help fast.</p>

<p><b>I have attached your full Performance Report.</b> I'll follow up with your office soon to see if you have any questions.</p>

<p>Best regards,</p>

<p><b>Daniel Coffman</b><br>
Owner, AI Service Co<br>
352-936-8152<br>
www.aiserviceco.com</p>

</body>
</html>
"""
    return html_body

def get_gmail_service():
    """Get authenticated Gmail service."""
    token_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_token.json"
    
    with open(token_path, "r") as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"]
    )
    
    return build("gmail", "v1", credentials=creds)

def send_bfisher_email(service, prospect, pdf_path):
    """Send bfisher-format email with PDF attachment."""
    
    msg = MIMEMultipart('mixed')
    
    # Subject
    subject = f"{prospect['company']} - Technical Health Audit of {prospect['website']}"
    
    # For preview, add preview header
    msg["Subject"] = f"[PREVIEW for {prospect['email']}] {subject}"
    msg["From"] = "Daniel Coffman <owner@aiserviceco.com>"
    msg["To"] = PREVIEW_EMAIL
    
    # Create HTML body
    html_body = create_bfisher_email(prospect)
    
    # Add preview header to body
    preview_header = f"""
<div style="background-color: #ffffd0; padding: 10px; margin-bottom: 20px; border: 2px solid #ffcc00;">
<b>PREVIEW EMAIL</b><br>
Original Recipient: {prospect['email']}<br>
Company: {prospect['company']}
</div>
"""
    full_html = preview_header + html_body
    
    msg.attach(MIMEText(full_html, 'html'))
    
    # Attach PDF
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf_part = MIMEBase('application', 'pdf')
            pdf_part.set_payload(f.read())
            encoders.encode_base64(pdf_part)
            
            pdf_filename = f"{prospect['company'].replace(' ', '_')}_Digital_Audit_{datetime.now().strftime('%b_%Y')}.pdf"
            pdf_part.add_header('Content-Disposition', f'attachment; filename="{pdf_filename}"')
            msg.attach(pdf_part)
            print(f"   📎 Attached: {pdf_filename}")
    
    # Encode and send
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    
    result = service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()
    
    return result

def main():
    print("=" * 70)
    print("SENDING BFISHER-FORMAT PREVIEW EMAILS")
    print("With: Traffic Light Table + PDF Audit Attachment")
    print("=" * 70)
    
    service = get_gmail_service()
    
    sent = 0
    failed = 0
    
    # Create temp directory for PDFs
    pdf_dir = tempfile.mkdtemp()
    
    for i, prospect in enumerate(PROSPECTS, 1):
        try:
            print(f"\n[{i}/10] Processing: {prospect['company']}...")
            
            # Generate PDF audit
            pdf_path = os.path.join(pdf_dir, f"audit_{i}.pdf")
            print(f"   📄 Generating PDF audit...")
            create_pdf_audit(prospect, pdf_path)
            
            # Send email with PDF
            print(f"   📧 Sending email...")
            result = send_bfisher_email(service, prospect, pdf_path)
            print(f"   ✅ Sent! Message ID: {result['id'][:20]}...")
            sent += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: {sent} sent, {failed} failed")
    print(f"Check nearmiss1193@gmail.com for preview emails")
    print("Format: HTML with Traffic Light Table + PDF Audit Attachment")
    print("=" * 70)

if __name__ == "__main__":
    main()
