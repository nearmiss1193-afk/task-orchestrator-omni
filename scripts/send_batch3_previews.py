#!/usr/bin/env python3
"""
Send Batch 3 Previews to Owner (Dan)
Follows strict /system_ops protocol:
1. Individual emails (mimics customer experience)
2. PDF Attachment included
3. Street Light HTML included
4. Tracking Pixel included
"""

import os
import sys
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DAN_EMAIL = "nearmiss1193@gmail.com"
HTML_DIR = r"C:\Users\nearm\.gemini\antigravity\brain\0b97dae9-c5c0-4924-8d97-793b59319985"
PDF_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\email_attachments\batch3"
TOKEN_PATH = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_token.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

PROSPECTS = [
    {
        "company": "Brilliant Smiles Lakeland",
        "email": "info@bslknd.com",
        "subject": "Brilliant Smiles Lakeland - Digital Performance Audit Results",
        "html_file": "batch3_email1_html.html",
        "pdf_name": "Audit_Brilliant_Smiles_Lakeland.pdf"
    },
    {
        "company": "Agnini Family Dental",
        "email": "info@agninidental.com",
        "subject": "Agnini Family Dental - Digital Performance Audit Results",
        "html_file": "batch3_email2_html.html",
        "pdf_name": "Audit_Agnini_Family_Dental.pdf"
    },
    {
        "company": "Markham Norton Mosteller Wright & Company",
        "email": "rsvp@markhamnorton.com",
        "subject": "Markham Norton - Digital Performance Audit Results",
        "html_file": "batch3_email3_html.html",
        "pdf_name": "Audit_Markham_Norton_Mosteller_Wright_and_Company.pdf"
    },
    {
        "company": "Monk Law Group",
        "email": "brian@monklawgroup.com",
        "subject": "Monk Law Group - Digital Performance Audit Results",
        "html_file": "batch3_email4_html.html",
        "pdf_name": "Audit_Monk_Law_Group.pdf"
    },
    {
        "company": "Watson Clinic LLP",
        "email": "HealthScene@WatsonClinic.com",
        "subject": "Watson Clinic LLP - Digital Performance Audit Results",
        "html_file": "batch3_email5_html.html",
        "pdf_name": "Audit_Watson_Clinic_LLP.pdf"
    },
    {
        "company": "GrayRobinson Lakeland",
        "email": "ben.lefrancois@gray-robinson.com",
        "subject": "GrayRobinson Lakeland - Digital Performance Audit Results",
        "html_file": "batch3_email6_html.html",
        "pdf_name": "Audit_GrayRobinson_Lakeland.pdf"
    },
    {
        "company": "Suncoast Skin Solutions",
        "email": "info@suncoastskin.com",
        "subject": "Suncoast Skin Solutions - Digital Performance Audit Results",
        "html_file": "batch3_email7_html.html",
        "pdf_name": "Audit_Suncoast_Skin_Solutions.pdf"
    },
    {
        "company": "Pansler Law Firm",
        "email": "karl@pansler.com",
        "subject": "Pansler Law Firm - Digital Performance Audit Results",
        "html_file": "batch3_email8_html.html",
        "pdf_name": "Audit_Pansler_Law_Firm.pdf"
    },
    {
        "company": "Dental Designs of Lakeland",
        "email": "info@dentaldesignslakeland.com",
        "subject": "Dental Designs of Lakeland - Digital Performance Audit Results",
        "html_file": "batch3_email9_html.html",
        "pdf_name": "Audit_Dental_Designs_of_Lakeland.pdf"
    },
    {
        "company": "MD Now Urgent Care",
        "email": "info@mymdnow.com",
        "subject": "MD Now Urgent Care Lakeland - Digital Performance Audit Results",
        "html_file": "batch3_email10_html.html",
        "pdf_name": "Audit_MD_Now_Urgent_Care.pdf"
    }
]

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("❌ Gmail Token Invalid/Expired. Cannot send.")
            sys.exit(1)
            
    return build('gmail', 'v1', credentials=creds)

def send_preview(service, prospect):
    msg = MIMEMultipart('mixed')
    
    # Subject clearly marked as PREVIEW
    msg['Subject'] = f"[PREVIEW] {prospect['subject']}"
    msg['From'] = "Daniel Coffman <owner@aiserviceco.com>"
    msg['To'] = DAN_EMAIL
    
    # Read HTML Body
    html_path = os.path.join(HTML_DIR, prospect['html_file'])
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"❌ HTML file not found: {html_path}")
        return False

    # Add Preview Header to Body
    preview_header = f"""
    <div style="background-color: #fef3c7; border: 2px solid #f59e0b; padding: 15px; margin-bottom: 20px; font-family: Arial;">
        <h3 style="margin:0; color: #92400e;">👀 PREVIEW MODE - BATCH 3</h3>
        <p style="margin: 5px 0;"><strong>Original Recipient:</strong> {prospect['email']}</p>
        <p style="margin: 5px 0;"><strong>Company:</strong> {prospect['company']}</p>
        <p style="margin: 5px 0;"><strong>Attached:</strong> {prospect['pdf_name']}</p>
    </div>
    <hr style="border: 0; border-top: 1px solid #ccc; margin: 20px 0;">
    """
    
    # Modify HTML to include preview header at the top of body
    final_html = html_content.replace("<body", "<body").replace(">", f">{preview_header}", 1)
    
    msg.attach(MIMEText(final_html, 'html'))
    
    # Attach PDF
    pdf_path = os.path.join(PDF_DIR, prospect['pdf_name'])
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{prospect["pdf_name"]}"')
            msg.attach(part)
    else:
        print(f"❌ PDF not found: {pdf_path}")
        return False

    # Attach PageSpeed Screenshot
    # Derive filename from PDF name: Audit_X.pdf -> PageSpeed_X.png
    png_name = prospect['pdf_name'].replace("Audit_", "PageSpeed_").replace(".pdf", ".png")
    png_path = os.path.join(PDF_DIR, png_name)
    
    if os.path.exists(png_path):
        with open(png_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{png_name}"')
            msg.attach(part)
    else:
        print(f"⚠️ PageSpeed PNG not found: {png_name}")

    # Attach Compliance Visual (Standard Placeholder)
    compliance_path = os.path.join(PDF_DIR, "Compliance_Footer_Missing.png")
    if os.path.exists(compliance_path):
        with open(compliance_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="Proof_Missing_Privacy_Policy.png"')
            msg.attach(part)
        
    # Send
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    try:
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        return True
    except Exception as e:
        print(f"❌ Gmail Error: {e}")
        return False

def main():
    print("="*60)
    print("SENDING BATCH 3 PREVIEWS TO OWNER")
    print("="*60)
    
    service = get_gmail_service()
    sent = 0
    failed = 0
    
    # PROSPECTS = PROSPECTS # Original full list
    # User requested ONE AT A TIME for approval.
    # Selecting ONLY the first prospect (Brilliant Smiles)
    target_prospect = [PROSPECTS[0]]
    
    for i, p in enumerate(target_prospect, 1):
        print(f"\n[{i}/10] {p['company']}...")
        if send_preview(service, p):
            print("   ✅ Sent Preview")
            sent += 1
        else:
            print("   ❌ Failed")
            failed += 1
            
    print("\n" + "="*60)
    print(f"COMPLETE: {sent} Sent, {failed} Failed")
    print(f"Check inbox: {DAN_EMAIL}")
    print("="*60)

if __name__ == "__main__":
    main()
