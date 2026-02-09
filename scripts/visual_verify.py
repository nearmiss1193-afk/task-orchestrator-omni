"""
VISUAL VERIFICATION WORKER — Owner Directive (Feb 9, 2026)
Replaces browser-based dashboard checks with API-level deep inspection.
Pulls ACTUAL data from Resend API + Supabase to produce comprehensive proof.
Equivalent to clicking through Resend dashboard + GHL contacts manually.
"""
import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv(".env")
load_dotenv(".env.local")

# === CONFIG ===
RESEND_KEY = os.getenv("RESEND_API_KEY", "")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
GHL_TOKEN = os.getenv("GHL_API_TOKEN", "")
GHL_LOCATION = os.getenv("GHL_LOCATION_ID", "")

OUTPUT_FILE = "scripts/visual_verify_output.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def check_resend():
    """Pull actual email data from Resend API — equivalent to viewing dashboard."""
    log("\n" + "=" * 60)
    log("  RESEND DASHBOARD (API Equivalent)")
    log("=" * 60)
    
    if not RESEND_KEY:
        log("  ERROR: RESEND_API_KEY not set")
        return
    
    headers = {"Authorization": f"Bearer {RESEND_KEY}"}
    
    # 1. Domains
    log("\n--- Verified Domains ---")
    r = requests.get("https://api.resend.com/domains", headers=headers, timeout=10)
    if r.status_code == 200:
        for d in r.json().get("data", []):
            name = d.get("name", "?")
            status = d.get("status", "?")
            region = d.get("region", "?")
            log(f"  {name} | status={status} | region={region}")
    else:
        log(f"  ERROR: HTTP {r.status_code}")
    
    # 2. Recent emails
    log("\n--- Recent Emails (Last 15) ---")
    r2 = requests.get("https://api.resend.com/emails", headers=headers, timeout=10)
    if r2.status_code == 200:
        emails = r2.json().get("data", [])
        log(f"  Total returned: {len(emails)}")
        
        delivered = 0
        bounced = 0
        opened = 0
        
        for e in emails[:15]:
            eid = e.get("id", "?")[:20]
            to_list = e.get("to", ["?"])
            to = to_list[0] if to_list else "?"
            subj = e.get("subject", "?")[:45]
            created = e.get("created_at", "?")[:19]
            sender = e.get("from", "?")
            last_event = e.get("last_event", "?")
            
            if last_event == "delivered":
                delivered += 1
            elif last_event == "bounced":
                bounced += 1
            elif last_event == "opened":
                opened += 1
            
            log(f"  {created} | {last_event:12s} | to={to}")
            log(f"    subject: {subj}")
            log(f"    from: {sender} | id: {eid}...")
        
        log(f"\n  Summary: delivered={delivered}, bounced={bounced}, opened={opened}")
    else:
        log(f"  ERROR: HTTP {r2.status_code} - {r2.text[:200]}")

    # 3. Get detail of most recent email for full proof
    if r2.status_code == 200 and emails:
        latest_id = emails[0].get("id")
        log(f"\n--- Detailed View: Most Recent Email ---")
        r3 = requests.get(f"https://api.resend.com/emails/{latest_id}", headers=headers, timeout=10)
        if r3.status_code == 200:
            detail = r3.json()
            log(f"  ID: {detail.get('id')}")
            log(f"  From: {detail.get('from')}")
            log(f"  To: {detail.get('to')}")
            log(f"  Subject: {detail.get('subject')}")
            log(f"  Created: {detail.get('created_at')}")
            log(f"  Last Event: {detail.get('last_event')}")
            # Check for HTML content (proves email had body)
            html = detail.get("html", "")
            if html:
                has_pixel = "track-email-open" in html or "eid=" in html
                log(f"  HTML Body: {len(html)} chars")
                log(f"  Tracking Pixel: {'YES' if has_pixel else 'NO'}")
            else:
                log(f"  HTML Body: EMPTY")


def check_supabase():
    """Pull outreach data from Supabase — equivalent to viewing database."""
    log("\n" + "=" * 60)
    log("  SUPABASE DATABASE (Live Data)")
    log("=" * 60)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        log("  ERROR: SUPABASE credentials not set")
        return
    
    from supabase import create_client
    s = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Today's outreach
    log("\n--- Today's Outreach Activity ---")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00")
    touches = s.table("outbound_touches").select("*").gte("ts", today).order("ts", desc=True).limit(20).execute()
    
    email_count = 0
    sms_count = 0
    with_variant = 0
    with_resend_id = 0
    
    for t in touches.data:
        ch = t.get("channel", "?")
        if ch == "email":
            email_count += 1
        elif ch == "sms":
            sms_count += 1
        
        vn = t.get("variant_name")
        if vn:
            with_variant += 1
        
        payload = t.get("payload") or {}
        if isinstance(payload, dict) and payload.get("resend_email_id"):
            with_resend_id += 1
    
    log(f"  Total touches today: {len(touches.data)}+")
    log(f"  Emails: {email_count} | SMS: {sms_count}")
    log(f"  With A/B variant: {with_variant}")
    log(f"  With Resend ID: {with_resend_id}")
    
    # Show last 5 with details
    log("\n--- Latest 5 Touches ---")
    for t in touches.data[:5]:
        ts = str(t.get("ts", "?"))[:19]
        ch = t.get("channel", "?")
        vn = t.get("variant_name") or "-"
        co = t.get("company") or "?"
        st = t.get("status") or "?"
        payload = t.get("payload") or {}
        rid = ""
        uid = ""
        if isinstance(payload, dict):
            rid = payload.get("resend_email_id", "")[:15]
            uid = payload.get("email_uid", "")
        log(f"  {ts} | ch={ch} | variant={vn} | {co}")
        log(f"    status={st} | resend_id={rid} | uid={uid}")
    
    # 2. A/B distribution
    log("\n--- A/B Variant Distribution ---")
    all_variants = s.table("outbound_touches").select("variant_name").eq("channel", "email").gte("ts", today).execute()
    dist = {}
    for v in all_variants.data:
        vn = v.get("variant_name") or "pre-AB"
        dist[vn] = dist.get(vn, 0) + 1
    for k, v in sorted(dist.items()):
        log(f"  {k}: {v} emails")
    
    # 3. Email opens
    log("\n--- Email Opens (Pixel Tracking) ---")
    opens = s.table("email_opens").select("*").order("opened_at", desc=True).limit(5).execute()
    log(f"  Recent opens: {len(opens.data)}")
    for o in opens.data:
        oa = str(o.get("opened_at", "?"))[:19]
        rec = o.get("recipient", "?")
        biz = o.get("business", "?")
        log(f"  {oa} | {rec} | {biz}")
    
    # 4. Lead status distribution
    log("\n--- Lead Status Distribution ---")
    for status in ["new", "research_done", "outreach_sent", "no_contact_info", "customer"]:
        count = s.table("contacts_master").select("id", count="exact").eq("status", status).execute()
        log(f"  {status}: {count.count}")
    
    # 5. Heartbeat
    log("\n--- System Heartbeat ---")
    hb = s.table("system_health_log").select("checked_at,status").order("checked_at", desc=True).limit(3).execute()
    for h in hb.data:
        log(f"  {str(h.get('checked_at','?'))[:19]} | {h.get('status','?')}")
    
    # 6. Campaign mode
    log("\n--- Campaign Mode ---")
    mode = s.table("system_state").select("*").eq("key", "campaign_mode").execute()
    for m in mode.data:
        log(f"  status={m.get('status','?')}")


def check_ghl():
    """Attempt GHL API — confirms ban status visually."""
    log("\n" + "=" * 60)
    log("  GHL API STATUS (Confirming Ban)")
    log("=" * 60)
    
    if not GHL_TOKEN:
        log("  GHL_API_TOKEN: NOT SET (confirms ban policy)")
        return
    
    headers = {
        "Authorization": f"Bearer {GHL_TOKEN}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    
    try:
        r = requests.get(
            f"https://services.leadconnectorhq.com/contacts/?locationId={GHL_LOCATION}&limit=1",
            headers=headers, timeout=10
        )
        log(f"  GET /contacts: HTTP {r.status_code}")
        if r.status_code == 401:
            log("  CONFIRMED: 401 Unauthorized — GHL API BAN is correct")
            log(f"  Response: {r.text[:200]}")
        elif r.status_code == 200:
            log("  WARNING: API returned 200 — ban may need re-evaluation")
        else:
            log(f"  Response: {r.text[:200]}")
    except Exception as e:
        log(f"  ERROR: {e}")


def main():
    # Clear output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"VISUAL VERIFICATION REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
    
    check_resend()
    check_supabase()
    check_ghl()
    
    log("\n" + "=" * 60)
    log("  VERIFICATION COMPLETE")
    log("=" * 60)


if __name__ == "__main__":
    main()
