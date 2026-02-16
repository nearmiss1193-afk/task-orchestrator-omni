import os, psycopg2, json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

def check_status():
    print("=" * 60)
    print(f"SUNDAY SYSTEM PULSE CHECK: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # 1. Heartbeats (Last 1 hour)
        print("\n[RECENT HEARTBEATS]")
        cur.execute("""
            SELECT checked_at, status, check_type 
            FROM public.system_health_log 
            WHERE checked_at > NOW() - INTERVAL '1 hour'
            ORDER BY checked_at DESC
        """)
        heartbeats = cur.fetchall()
        if not heartbeats:
            print("  ❌ NO HEARTBEATS in last hour!")
        else:
            for hb in heartbeats:
                print(f"  - [{hb[0]}] {hb[1]:10} | {hb[2]}")
        
        # 2. Outreach (Last 12 hours) - Should be mostly Email
        print("\n[RECENT OUTREACH (Last 12h)]")
        cur.execute("""
            SELECT ts, channel, status, variant_id
            FROM public.outbound_touches 
            WHERE ts > NOW() - INTERVAL '12 hours'
            ORDER BY ts DESC LIMIT 10
        """)
        touches = cur.fetchall()
        if not touches:
            print("  ℹ️ No outreach in last 12 hours.")
        else:
            for t in touches:
                print(f"  - [{t[0]}] {t[1]:8} | {t[2]:12} | {t[3]}")
        
        # 3. Research Progress
        print("\n[RESEARCH STRIKE PROGRESS]")
        cur.execute("SELECT status, count(*) FROM public.contacts_master GROUP BY status")
        counts = dict(cur.fetchall())
        for s, c in counts.items():
            print(f"  - {s:20}: {c}")
            
        cur.execute("SELECT count(*) FROM public.contacts_master WHERE status = 'new' AND website_url IS NOT NULL")
        new_with_web = cur.fetchone()[0]
        print(f"  - Leads ('new') with website_url: {new_with_web}")
            
        # 4. Check for today's SMS/Calls (Sunday - Should be 0)
        print("\n[SUNDAY RESTRICTION CHECK]")
        cur.execute("""
            SELECT count(*) 
            FROM public.outbound_touches 
            WHERE channel IN ('sms', 'call') 
            AND ts > date_trunc('day', NOW())
        """)
        sunday_restricted = cur.fetchone()[0]
        if sunday_restricted > 0:
            print(f"  ⚠️ ALERT: {sunday_restricted} SMS/Calls sent today (Sunday)!")
        else:
            print("  ✅ Sunday restrictions respected: 0 SMS/Calls sent.")

        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

if __name__ == "__main__":
    check_status()
