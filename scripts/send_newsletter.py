"""SEND NEWSLETTER #1 — Live deployment via Resend"""
import os
import sys
import time
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
from supabase import create_client
import resend

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

resend.api_key = os.getenv("RESEND_API_KEY")

# Import newsletter generator
sys.path.insert(0, 'workers')
from newsletter import generate_newsletter

def send_first_newsletter():
    print("=" * 60)
    print("  NEWSLETTER #1 — LIVE SEND")
    print("=" * 60)
    
    # Generate newsletter
    nl = generate_newsletter(edition=0)
    print(f"Subject: {nl['subject']}")
    
    # Get recipients (all with email, not unsubscribed/customer)
    recipients = supabase.table("contacts_master") \
        .select("id,email,company_name") \
        .neq("status", "unsubscribed") \
        .neq("status", "customer") \
        .not_.is_("email", "null") \
        .execute()
    
    valid = [r for r in (recipients.data or []) if r.get("email") and "@" in r.get("email", "")]
    print(f"Eligible recipients: {len(valid)}")
    
    if not valid:
        print("No recipients found!")
        return
    
    sent = 0
    errors = 0
    
    for r in valid:
        email = r["email"]
        company = r.get("company_name", "Business Owner")
        
        try:
            result = resend.Emails.send({
                "from": "Dan Coffman <dan@aiserviceco.com>",
                "to": [email],
                "subject": nl["subject"],
                "html": nl["html"],
            })
            sent += 1
            print(f"  ✅ Sent to: {email}")
            
            # Log to outbound_touches
            try:
                supabase.table("outbound_touches").insert({
                    "lead_id": r["id"],
                    "channel": "email",
                    "touch_type": "newsletter_1",
                    "content_preview": nl["subject"][:100],
                }).execute()
            except Exception:
                pass
            
            time.sleep(0.3)  # Rate limiting for Resend
            
        except Exception as e:
            errors += 1
            print(f"  ❌ Failed: {email} — {e}")
    
    print(f"\n{'=' * 60}")
    print(f"  NEWSLETTER #1 RESULTS")
    print(f"{'=' * 60}")
    print(f"  Sent: {sent}")
    print(f"  Errors: {errors}")
    print(f"  Subject: {nl['subject']}")
    
    return sent


if __name__ == "__main__":
    send_first_newsletter()
