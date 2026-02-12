"""Test email dispatch on a single outreach_sent lead"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client
import requests
import uuid
import random

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Get one outreach_sent lead with email
lead = sb.table("contacts_master") \
    .select("*") \
    .eq("status", "outreach_sent") \
    .neq("email", "") \
    .limit(1).execute()

if not lead.data:
    print("NO LEADS FOUND")
    exit()

l = lead.data[0]
print(f"Lead: {l.get('company_name','?')}")
print(f"Email: {l.get('email','?')}")
print(f"Phone: {l.get('phone','?')}")
print(f"Status: {l.get('status','?')}")

# Check if email is placeholder
email = l["email"]
skip_patterns = ['placeholder', 'test@', 'demo.com', 'funnel.com', 'example.com', 'unassigned']
if any(p in email.lower() for p in skip_patterns):
    print(f"SKIP: placeholder email: {email}")
    exit()

# Check touch count
prior = sb.table("outbound_touches") \
    .select("ts,variant_name", count="exact") \
    .eq("channel", "email") \
    .eq("phone", l.get("phone")) \
    .order("ts", desc=True) \
    .execute()
print(f"Touch count (by phone): {prior.count}")
if prior.data:
    print(f"Last touch: {prior.data[0].get('ts')}")

# Also check by company
if prior.count == 0 and l.get("company_name"):
    prior2 = sb.table("outbound_touches") \
        .select("ts", count="exact") \
        .eq("channel", "email") \
        .eq("company", l.get("company_name")) \
        .order("ts", desc=True) \
        .execute()
    print(f"Touch count (by company): {prior2.count}")
    if prior2.data:
        print(f"Last touch (company): {prior2.data[0].get('ts')}")

# Try sending via Resend
resend_key = os.getenv("RESEND_API_KEY")
print(f"\nResend key present: {'YES' if resend_key else 'NO'}")

first_name = (l.get("full_name") or "there").split(" ")[0]
company = l.get("company_name") or "your company"

subject = f"Quick follow-up about {company}"
body = f"""Hi {first_name},

Just following up on my earlier note about {company}.

I work with local businesses to help them get found online. Happy to share some specific suggestions that could help drive more customers your way.

Worth a quick 5-min chat?

Best,
Dan"""

email_uid = str(uuid.uuid4())[:8]

payload = {
    "from": "Dan <dan@aiserviceco.com>",
    "to": [email],
    "subject": subject,
    "html": f"<div style='font-family:Arial;font-size:14px;color:#333;line-height:1.6'>{body.replace(chr(10),'<br>')}</div>",
}

print(f"\nSending test email to: {email}")
print(f"Subject: {subject}")

r = requests.post(
    "https://api.resend.com/emails",
    headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
    json=payload,
    timeout=15
)

print(f"Resend status: {r.status_code}")
print(f"Response: {r.text[:300]}")

if r.status_code in [200, 201]:
    print("\nEMAIL SENT SUCCESSFULLY!")
    # Log it
    sb.table("outbound_touches").insert({
        "phone": l.get("phone"),
        "channel": "email",
        "company": company,
        "status": "sent",
        "correlation_id": r.json().get("id", ""),
        "payload": {"to": email, "subject": subject, "test": True}
    }).execute()
    print("Logged to outbound_touches")
else:
    print(f"\nEMAIL FAILED: {r.status_code}")
