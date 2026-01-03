import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Optional: Import Resend or SendGrid SDK if installed
# import resend 

def send_email_direct(to_email, subject, body_html, from_email="system@aiserviceco.com", provider="SMTP"):
    """
    Sends an email directly via SMTP or API (Resend/SendGrid).
    Fallback/Redundancy Layer.
    """
    print(f"📧 Sending Direct Email to {to_email} via {provider}...")
    
    if provider == "SMTP":
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")
        
        if not smtp_user or not smtp_pass:
            print("⚠️ SMTP Credentials Missing. Using Simulation Mode.")
            return {"status": "simulated", "provider": "SMTP (Mock)"}
            
        try:
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body_html, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            print("✅ Email Sent Successfully (SMTP).")
            return {"status": "sent", "provider": "SMTP"}
            
        except Exception as e:
            print(f"❌ SMTP Error: {e}")
            return {"status": "error", "message": str(e)}

    elif provider == "RESEND":
        # Placeholder for Resend API
        # resend.api_key = os.environ.get("RESEND_API_KEY")
        # r = resend.Emails.send(...)
        return {"status": "not_implemented", "provider": "Resend"}
        
    return {"status": "error", "message": "Unknown Provider"}
