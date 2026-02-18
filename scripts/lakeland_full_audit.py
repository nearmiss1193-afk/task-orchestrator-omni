"""
Lakeland Full System Audit - Plain ASCII output
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
from supabase import create_client
import requests

lines = []
def log(msg):
    lines.append(msg)

def main():
    log("=" * 60)
    log("  LAKELAND FULL SYSTEM AUDIT")
    log("=" * 60)
    
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    sb = create_client(sb_url, sb_key)
    
    # Total contacts
    total = sb.table("contacts_master").select("id", count="exact").execute()
    log(f"\n[SUPABASE] contacts_master")
    log(f"   Total leads: {total.count}")
    
    # Lakeland-sourced
    lakeland = sb.table("contacts_master").select("id", count="exact").eq("source", "lakeland_finds").execute()
    log(f"   Lakeland-sourced: {lakeland.count}")
    
    # With email
    with_email = sb.table("contacts_master").select("id", count="exact").neq("email", "").execute()
    log(f"   With email: {with_email.count}")
    
    # With phone
    with_phone = sb.table("contacts_master").select("id", count="exact").neq("phone", "").execute()
    log(f"   With phone: {with_phone.count}")
    
    # Status breakdown
    statuses = sb.table("contacts_master").select("status").execute()
    status_counts = {}
    for r in statuses.data:
        s = r.get("status", "null")
        status_counts[s] = status_counts.get(s, 0) + 1
    log(f"\n   Status breakdown:")
    for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
        log(f"     {s}: {c}")
    
    # SlyBroadcasting priority owners
    log(f"\n[SLY BROADCASTING] Priority Owner Check")
    lakeland_leads = sb.table("contacts_master").select("id,company_name,phone,raw_research").eq("source", "lakeland_finds").limit(2000).execute()
    
    priority_count = 0
    priority_with_phone = 0
    for r in lakeland_leads.data:
        rr = r.get("raw_research")
        if not rr: continue
        if isinstance(rr, str):
            try: rr = json.loads(rr)
            except: continue
        if isinstance(rr, dict) and rr.get("is_priority_owner"):
            priority_count += 1
            if r.get("phone"):
                priority_with_phone += 1
    
    log(f"   Leads with is_priority_owner flag: {priority_count}")
    log(f"   Priority owners WITH phone: {priority_with_phone}")
    if priority_count == 0:
        log(f"   WARNING: Owner identification has NOT run yet")
    
    # VAPI
    log(f"\n[VAPI] Phone Number Check")
    vapi_key = os.environ.get("VAPI_PRIVATE_KEY")
    vapi_phone_id = os.environ.get("VAPI_PHONE_NUMBER_ID")
    log(f"   VAPI_PHONE_NUMBER_ID: {vapi_phone_id or 'NOT SET'}")
    
    if vapi_key and vapi_phone_id:
        try:
            r = requests.get(
                f"https://api.vapi.ai/phone-number/{vapi_phone_id}",
                headers={"Authorization": f"Bearer {vapi_key}"},
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                log(f"   ACTIVE: {data.get('number', 'unknown')}")
                log(f"   Provider: {data.get('provider', 'unknown')}")
                log(f"   Name: {data.get('name', 'unnamed')}")
            else:
                log(f"   FAILED: HTTP {r.status_code} - {r.text[:200]}")
        except Exception as e:
            log(f"   ERROR: {e}")
    
    # NEON
    log(f"\n[LAKELANDFINDS.COM] Neon Business Count")
    neon_url = os.environ.get("NEON_DATABASE_URL")
    
    if neon_url:
        try:
            import psycopg2
            conn = psycopg2.connect(neon_url)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM businesses")
            count = cur.fetchone()[0]
            log(f"   Total businesses in Neon: {count}")
            
            cur.execute("SELECT category, COUNT(*) as cnt FROM businesses GROUP BY category ORDER BY cnt DESC LIMIT 10")
            rows = cur.fetchall()
            if rows:
                log(f"   Top categories:")
                for cat, cnt in rows:
                    log(f"     {cat or 'uncategorized'}: {cnt}")
            
            cur.execute("SELECT COUNT(*) FROM businesses WHERE vibe_summary IS NOT NULL")
            enriched = cur.fetchone()[0]
            log(f"   With vibe_summary: {enriched}/{count}")
            
            cur.close()
            conn.close()
        except Exception as e:
            log(f"   Neon error: {e}")
            neon_url = None
    
    if not neon_url:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lakeland_businesses_enriched.csv")
        if os.path.exists(csv_path):
            import csv
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            log(f"   Local CSV (lakeland_businesses_enriched.csv): {len(rows)} businesses")
            we = sum(1 for r in rows if r.get('email'))
            wp = sum(1 for r in rows if r.get('phone'))
            log(f"      With email: {we}")
            log(f"      With phone: {wp}")
    
    # Outreach
    log(f"\n[OUTREACH] Recent Activity")
    try:
        recent = sb.table("outbound_touches").select("id", count="exact").gte("ts", "2026-02-17T00:00:00").execute()
        log(f"   Outreach since 2/17: {recent.count}")
        all_time = sb.table("outbound_touches").select("id", count="exact").execute()
        log(f"   All-time outreach: {all_time.count}")
    except Exception as e:
        log(f"   Error: {e}")
    
    log("\n" + "=" * 60)
    log("  AUDIT COMPLETE")
    log("=" * 60)
    
    # Write to file
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_result.txt")
    with open(out, 'w', encoding='ascii', errors='replace') as f:
        f.write("\n".join(lines))
    
    # Also print
    for l in lines:
        print(l, flush=True)

if __name__ == "__main__":
    main()
