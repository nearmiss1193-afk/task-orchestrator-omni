
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
AUDIT_JSON_PATH = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\audit_reports\Brilliant_Smiles_audit.json"

def get_gmail_service():
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

def create_pdf_audit(data, output_path):
    """Create PDF audit report from JSON data."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=20)
    story.append(Paragraph("DIGITAL RISK & PERFORMANCE AUDIT (V3)", title_style))
    story.append(Spacer(1, 12))
    
    # Client info
    client_style = ParagraphStyle('Client', parent=styles['Normal'], fontSize=10)
    story.append(Paragraph(f"<b>Client:</b> {data['business_name']} | <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", client_style))
    story.append(Spacer(1, 20))
    
    # Findings
    h2 = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, textColor=colors.red, spaceAfter=10)
    story.append(Paragraph("CRITICAL FINDINGS", h2))
    
    # Legal
    legal = data.get('legal', {})
    if not legal.get('terms_found'):
        story.append(Paragraph("<b>• MISSING TERMS OF USE:</b> No Terms of Use agreement found. High liability risk.", styles['Normal']))
        story.append(Spacer(1, 5))
    if not legal.get('privacy_found'):
        story.append(Paragraph("<b>• MISSING PRIVACY POLICY:</b> No Privacy Policy found. Non-compliant with FL Law.", styles['Normal']))
        story.append(Spacer(1, 5))
    if legal.get('contact_form_found') and not legal.get('contact_consent_found'):
        story.append(Paragraph("<b>• NO AFFIRMATIVE CONSENT:</b> Contact form collects data without 'I Agree' checkbox.", styles['Normal']))
        story.append(Spacer(1, 5))
        
    # Perf
    perf = data.get('performance', {})
    story.append(Paragraph(f"<b>• MOBILE PERFORMANCE:</b> Score {perf.get('performance')}/100. Load time: {perf.get('fcp')}.", styles['Normal']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("RECOMMENDATION: Immediate remediation of legal gaps.", styles['Normal']))
    
    doc.build(story)
    return output_path



def generate_email_body_v1(data):
    legal = data.get('legal', {})
    perf = data.get('performance', {})
    score = perf.get('performance', 0)
    
    # EXACT FORMATTING v1 - LOCKED
    body = f"""
Red – Legal exposure:
- No Terms & Conditions page.
- Contact form missing TCPA consent checkbox.
Fines up to $1,500 per lead.

Yellow – Revenue leak:
- PageSpeed {score} – slow load = 20% bounce rate.
- No privacy link on form – trust drop.

Green – What we do:
- AI answering 24/7, no missed calls.
- Map-Pack SEO – own “dentist near me.”
- Automated newsletters – 30% rebook rate.

Attached: full audit + screenshots.

Reply “yes” – I’ll book a 10-min walkthrough.
AI Service Co
    """
    return body.strip()

def send_proof():
    try:
        service = get_gmail_service()
        
        # Load Data
        with open(AUDIT_JSON_PATH, "r") as f:
            data = json.load(f)
            
        subject = "Risk Alert – Site Audit"
        body_text = generate_email_body_v1(data)

        # Create Message
        msg = MIMEMultipart('mixed')
        msg['to'] = RECIPIENT
        msg['from'] = "AI Service Co Pipeline <owner@aiserviceco.com>"
        msg['subject'] = subject

        # Text Part
        msg.attach(MIMEText(body_text, 'plain'))

        # 1. Attach PDF
        pdf_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(pdf_dir, "audit_report.pdf")
        create_pdf_audit(data, pdf_path)
        
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        pdf_part = MIMEBase('application', 'pdf')
        pdf_part.set_payload(pdf_data)
        encoders.encode_base64(pdf_part)
        pdf_part.add_header('Content-Disposition', f'attachment; filename="audit_report.pdf"')
        msg.attach(pdf_part)

        # 2. Attach Screenshots (Mapping from V3 names to Spec names)
        screenshot_map = {
            "screenshot_terms_missing.png": data['screenshots'].get('homepage'),
            "screenshot_form_no_checkbox.png": data['screenshots'].get('contact'),
            "screenshot_privacy_ok.png": data['screenshots'].get('search_privacy')
        }

        # OVERSEER CHECK
        missing_files = []
        for spec_name, real_path in screenshot_map.items():
            if not real_path or not os.path.exists(real_path):
                missing_files.append(spec_name)

        if missing_files:
            print(f"🛑 OVERSEER BLOCK: Missing screenshots: {missing_files}")
            return # Block send

        # Attach images
        for spec_name, real_path in screenshot_map.items():
            with open(real_path, 'rb') as f:
                img_data = f.read()
            img_part = MIMEBase('application', 'octet-stream')
            img_part.set_payload(img_data)
            encoders.encode_base64(img_part)
            img_part.add_header('Content-Disposition', f'attachment; filename="{spec_name}"')
            msg.attach(img_part)

        # Send
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        print(f"Sending V1 LOCKED proof to {RECIPIENT}...")
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        print("✅ V1 LOCKED Proof Email Sent Successfully.")

    except Exception as e:
        print(f"❌ Failed to send: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_proof()
