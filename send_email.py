import os
import sys
import resend
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not all([RESEND_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    print("FATAL: Missing env vars")
    sys.exit(1)

import requests
from supabase import create_client, Client

# Restore Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_intro_email(lead_id, company, email, contact_name="there"):
    print(f"[{lead_id}] Sending intro email to {email}...")
    
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    html_content = f"""
    <div style="font-family: sans-serif; color: #333;">
    <p>Hey {contact_name},</p>
    <p>Quick question - are you guys getting flooded with calls, or just regular busy right now?</p>
    <p>I know storm season gets crazy. We have an AI receptionist system that picks up 24/7, books estimates, and texts you the details instantly. Costs less than one booked job.</p>
    <p>I'll give you a quick call in a few minutes to see if we can help.</p>
    <p>Best,<br>
    John<br>
    AI Service Company</p>
    </div>
    """

    payload = {
        "from": "John <onboarding@resend.dev>", 
        "to": [email],
        "subject": f"Quick question about {company}",
        "html": html_content
    }

    try:
        r = requests.post(url, headers=headers, json=payload)
        
        if r.status_code in [200, 201]:
            print(f"[{lead_id}] Email sent! ID: {r.json().get('id')}")
            # Update DB
            supabase.table("leads").update({
                "status": "warming_up",
                "email_sent_at": datetime.now().isoformat()
            }).eq("id", lead_id).execute()
            return True
        else:
            raise Exception(f"Status {r.status_code}: {r.text}")

    except Exception as e:
        print(f"[{lead_id}] Email FAILED: {e}")
        # Mark as ready_to_call anyway to not stall pipeline
        supabase.table("leads").update({
            "status": "ready_to_call", 
            "notes": f"Email failed: {str(e)}"
        }).eq("id", lead_id).execute()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python send_email.py <lead_id> <company> <email>")
        sys.exit(1)
    
    send_intro_email(sys.argv[1], sys.argv[2], sys.argv[3])
