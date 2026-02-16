import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_audit():
    print("=" * 60)
    print("REVENUE WATERFALL AUDIT (DIRECT POSTGRES)")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Check current db and search path
        cur.execute("SELECT current_database(), current_schemas(false)")
        db_info = cur.fetchone()
        print(f"DB: {db_info[0]} | Search Path: {db_info[1]}")
        
        # 1. Sending (24h)
        cur.execute('SELECT COUNT(*) FROM public.outbound_touches WHERE ts > NOW() - INTERVAL \'24 hours\'')
        sending_24h = cur.fetchone()[0]
        
        # 2. Opening (7d)
        cur.execute('SELECT COUNT(*) FROM public.outbound_touches WHERE opened = true AND ts > NOW() - INTERVAL \'7 days\'')
        opening_7d = cur.fetchone()[0]
        
        # 3. Replying (7d)
        cur.execute('SELECT COUNT(*) FROM public.outbound_touches WHERE replied = true AND ts > NOW() - INTERVAL \'7 days\'')
        replying_7d = cur.fetchone()[0]
        
        # 4. Pipeline Status
        cur.execute('SELECT status, COUNT(*) FROM public.contacts_master GROUP BY status')
        pipeline = dict(cur.fetchall())
        
        # 5. Recent Activity
        cur.execute('SELECT ts, channel, status FROM public.outbound_touches ORDER BY ts DESC LIMIT 10')
        recent = cur.fetchall()
        
        print(f"\n[WATERFALL METRICS]")
        print(f"  Sending (24h):  {sending_24h}")
        print(f"  Opening (7d):   {opening_7d}")
        print(f"  Replying (7d):  {replying_7d}")
        print(f"\n[PIPELINE HEALTH]")
        for status, count in pipeline.items():
            print(f"  {status:20}: {count}")
            
        print(f"\n[RECENT TOUCHES]")
        for i, (ts, channel, status) in enumerate(recent):
            print(f"  {i+1}. [{ts}] {channel:8} | {status}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

if __name__ == "__main__":
    run_audit()
