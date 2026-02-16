import os
import json
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def final_audit_pull():
    print("=" * 60)
    print("FINAL WATERFALL PULL")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # 1. Sending (24h)
        cur.execute("SELECT COUNT(*) FROM public.outbound_touches WHERE ts > NOW() - INTERVAL '24 hours'")
        s24 = cur.fetchone()[0]
        
        # 2. Pipeline Health
        cur.execute("SELECT status, COUNT(*) FROM public.contacts_master GROUP BY status")
        pipe = dict(cur.fetchall())
        
        # 3. Recent Touches
        cur.execute("SELECT ts, channel, status FROM public.outbound_touches ORDER BY ts DESC LIMIT 10")
        recent = cur.fetchall()
        
        # 4. Check for 'opened' and 'replied' values in status or payload
        # Since the column check mentioned 'opened' and 'replied' were columns, but maybe they aren't booleans? 
        # Let's check status values.
        cur.execute("SELECT status, COUNT(*) FROM public.outbound_touches GROUP BY status")
        outbound_statuses = dict(cur.fetchall())
        
        print(f"\n[METRICS]")
        print(f"  Sending (24h):  {s24}")
        print(f"\n[PIPELINE]")
        for s, c in pipe.items(): print(f"  {s:15}: {c}")
            
        print(f"\n[OUTBOUND STATUSES]")
        for s, c in outbound_statuses.items(): print(f"  {s:15}: {c}")
            
        print(f"\n[RECENT]")
        for r in recent: print(f"  {r}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    final_audit_pull()
