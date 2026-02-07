
import os
import json
import base64
import tempfile
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ReportLab Imports
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import red, orange, green, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

# Configuration
TOKEN_PATH = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_token.json"
RECIPIENT = "nearmiss1193@gmail.com"
SUBJECT = "PROOF DB: Full Packet (HTML + PDF Attachment)"
HTML_PATH = r"C:\Users\nearm\.gemini\antigravity\brain\0b97dae9-c5c0-4924-8d97-793b59319985\batch3_email1_html.html"

# Dummy Prospect Data for PDF
PROSPECT = {
    "company": "Brilliant Smiles Lakeland",
    "website": "yourlakelanddentist.com",
    "industry": "Dentist",
    "city": "Lakeland",
    "mobile_status": "CRITICAL",
    "load_time": "4.2",
    "security_status": "WARNING",
    "ssl_status": "Valid but insecure forms"
}

def get_gmail_service():
    """Get authenticated Gmail service using existing token."""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token not found at {TOKEN_PATH}")
        
    with open(TOKEN_PATH, "r") as f:
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

def create_pdf_audit(prospect, output_path):
    """Create PDF audit report."""
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
    
    # Mobile Speed finding
    story.append(Paragraph(f"<b>• Mobile Performance Status: {prospect['mobile_status']} ({prospect['load_time']}s)</b>", styles['Normal']))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"<b>• Primary Issue: Excessive Load Time ({prospect['load_time']} seconds):</b> The Google PageSpeed test matrix shows the main content takes {prospect['load_time']} seconds to appear on mobile devices. Emergency {prospect['industry']} customers searching on their phones will abandon your site before it even appears.", styles['Normal']))
    story.append(Spacer(1, 10))

    # Security finding
    story.append(Paragraph(f"<b>• Security Risk: {prospect['security_status']}:</b> {prospect['ssl_status']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Solutions
    story.append(Paragraph("PROPOSED SOLUTIONS", heading_style))
    solutions = [
        f"<b>1. Emergency Performance Recovery:</b> Reduce mobile load time to under 3s.",
        f"<b>2. Legal Compliance Upgrade:</b> Install Terms of Use & Contact Form Consent.",
        f"<b>3. AI-Powered Phone System:</b> Capture leads 24/7."
    ]
    for s in solutions:
        story.append(Paragraph(s, styles['Normal']))
        story.append(Spacer(1, 5))
    
    doc.build(story)
    return output_path

def send_proof():
    try:
        service = get_gmail_service()
        
        # Read HTML
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # PROOF HEADER
        header = f"""
        <div style="background-color: #ffffd0; padding: 10px; margin-bottom: 20px; border: 2px solid #ffcc00; font-family: sans-serif;">
            <strong>🛑 PROOF MODE (WITH ATTACHMENT)</strong><br>
            Attached: Audit Report PDF<br>
            <strong>Subject:</strong> {SUBJECT}
        </div>
        """
        full_body = header + html_content

        # Create Message
        msg = MIMEMultipart('mixed')
        msg['to'] = RECIPIENT
        msg['from'] = "AI Service Co Proof <owner@aiserviceco.com>"
        msg['subject'] = SUBJECT

        # HTML Part
        html_part = MIMEText(full_body, 'html')
        msg.attach(html_part)

        # Generate & Attach PDF
        pdf_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(pdf_dir, "Brilliant_Smiles_Audit.pdf")
        print("Generating PDF...")
        create_pdf_audit(PROSPECT, pdf_path)
        
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            
        pdf_part = MIMEBase('application', 'pdf')
        pdf_part.set_payload(pdf_data)
        encoders.encode_base64(pdf_part)
        pdf_part.add_header('Content-Disposition', f'attachment; filename="Brilliant_Smiles_Audit.pdf"')
        msg.attach(pdf_part)
        print("PDF Attached.")

        # Send
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        print(f"Sending proof to {RECIPIENT}...")
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        print("✅ Proof Email Sent Successfully (via Gmail API).")

    except Exception as e:
        print(f"❌ Failed to send: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_proof()
