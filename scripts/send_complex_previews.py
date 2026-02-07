
import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

try:
    from scripts.gmail_api_sender import get_gmail_service
except ImportError:
    from gmail_api_sender import get_gmail_service


def send_complex_email_api(to_email, subject, html_content, attachments_dict=None):
    """
    Send a complex email using the Gmail API (OAuth) and MIME architecture.
    """
    print(f"🚀 Preparing email to {to_email}...")

    # Authenticate using existing validated credentials
    try:
        service = get_gmail_service()
    except Exception as e:
        print(f"❌ Auth Failed: {e}")
        return False

    FROM_EMAIL = "owner@aiserviceco.com"

    # Create the root message container (MIMEMultipart 'mixed')
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = f"Daniel Coffman <{FROM_EMAIL}>"
    msg['To'] = to_email

    # Create a 'related' container for HTML and inline images
    msg_related = MIMEMultipart('related')
    msg.attach(msg_related)

    # Attach the HTML content
    html_part = MIMEText(html_content, 'html')
    msg_related.attach(html_part)

    # Handle inline images
    if attachments_dict and 'inline_images' in attachments_dict:
        for cid, image_path in attachments_dict['inline_images'].items():
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-ID', f'<{cid}>')
                    img.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
                    msg_related.attach(img)
            else:
                 print(f"⚠️ Warning: Inline image not found: {image_path}")

    # Handle file attachments
    if attachments_dict and 'files' in attachments_dict:
        for filename, filepath in attachments_dict['files'].items():
            if os.path.exists(filepath):
                with open(filepath, 'rb') as file:
                    if filename.lower().endswith('.pdf'):
                        attachment = MIMEApplication(file.read(), _subtype="pdf")
                    else:
                        attachment = MIMEApplication(file.read())
                    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                    msg.attach(attachment)
                    print(f"   📎 Attached: {filename}")
            else:
                print(f"❌ Error: Attachment file not found: {filepath}")

    # Encode for Gmail API
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

    # Send
    try:
        sent = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f"✅ Email sent successfully! ID: {sent['id']}")
        return True
    except Exception as e:
        print(f"❌ API Send Failed: {str(e)}")
        return False

if __name__ == "__main__":
    # CONFIGURATION FOR BRILLIANT SMILES
    RECIPIENT = "nearmiss1193@gmail.com"
    SUBJECT = "[PREVIEW HTML] Brilliant Smiles Lakeland - Digital Performance Audit Results"
    
    # Paths
    BASE_DIR = r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified"
    BRAIN_DIR = r"C:\Users\nearm\.gemini\antigravity\brain\0b97dae9-c5c0-4924-8d97-793b59319985"
    
    HTML_PATH = os.path.join(BRAIN_DIR, "batch3_email1_html.html")
    PAGESPEED_PATH = os.path.join(BASE_DIR, "email_attachments", "batch3", "PageSpeed_Brilliant_Smiles_Lakeland.png")
    EVIDENCE_PATH = os.path.join(BASE_DIR, "evidence", "evidence_Brilliant_Smiles_Lakeland.png")
    PDF_PATH = os.path.join(BASE_DIR, "email_attachments", "batch3", "Audit_Brilliant_Smiles_Lakeland.pdf")

    # Read HTML
    try:
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: HTML file not found at {HTML_PATH}")
        exit(1)
    
    attachments = {
        'files': {
            'Audit_Brilliant_Smiles_Lakeland.pdf': PDF_PATH,
            'PageSpeed_Report.png': PAGESPEED_PATH,
            'Evidence_Missing_Privacy.png': EVIDENCE_PATH
        }
    }

    send_complex_email_api(RECIPIENT, SUBJECT, html_content, attachments)

