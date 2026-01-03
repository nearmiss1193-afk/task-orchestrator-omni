
import os
from dotenv import load_dotenv

load_dotenv()

email = os.environ.get("GHL_EMAIL")
resend_key = os.environ.get("RESEND_API_KEY")

print(f"GHL_EMAIL: {email}")
print(f"RESEND_API_KEY: {'[FOUND]' if resend_key else '[MISSING]'}")

smtp_user = os.environ.get("SMTP_USER")
smtp_pass = os.environ.get("SMTP_PASS")

print(f"SMTP_USER: {'[FOUND]' if smtp_user else '[MISSING]'}")
print(f"SMTP_PASS: {'[FOUND]' if smtp_pass else '[MISSING]'}")
