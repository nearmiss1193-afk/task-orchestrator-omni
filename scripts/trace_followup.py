"""Trace follow-up eligibility - fixed"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client
from datetime import datetime, timezone, timedelta

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

leads = sb.table("contacts_master") \
    .select("id,email,phone,company_name,status") \
    .eq("status", "outreach_sent") \
    .neq("email", "") \
    .limit(5).execute()

day3 = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()

for l in leads.data or []:
    lead_id = l["id"]
    email = l.get("email", "?")
    phone = l.get("phone") or ""
    company = l.get("company_name") or "?"
    
    skip_patterns = ['placeholder', 'test@', 'demo.com', 'funnel.com', 'example.com', 'unassigned']
    if any(p in email.lower() for p in skip_patterns):
        print(f"SKIP: {company[:25]} | placeholder: {email}")
        continue
    
    touch_count = 0
    last_ts = None
    
    if phone:
        try:
            p = sb.table("outbound_touches").select("ts", count="exact").eq("channel","email").eq("phone",phone).order("ts",desc=True).execute()
            touch_count = p.count if p.count else 0
            if p.data:
                last_ts = p.data[0].get("ts")
        except:
            pass
    
    if touch_count == 0 and company and company != "?":
        try:
            p2 = sb.table("outbound_touches").select("ts", count="exact").eq("channel","email").eq("company",company).order("ts",desc=True).execute()
            touch_count = p2.count if p2.count else 0
            if p2.data:
                last_ts = p2.data[0].get("ts")
        except:
            pass
    
    if touch_count >= 3:
        v = "SEQ_COMPLETE"
    elif last_ts and last_ts > day3:
        v = "TOO_RECENT"
    elif touch_count == 0 and not last_ts:
        v = "ELIGIBLE (no prior touches found)"
    else:
        step = touch_count + 1
        v = f"ELIGIBLE step={step}"
    
    print(f"{company[:25]:25s} | email={email[:25]:25s} | touches={touch_count} | last={str(last_ts)[:16] if last_ts else 'NEVER':16s} | {v}")
