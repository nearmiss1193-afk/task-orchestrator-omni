import os, psycopg2
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

def audit_outreach():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        print("--- LAST 50 OUTREACH TOUCHES ---")
        cur.execute("""
            SELECT ts, channel, status, company, variant_id 
            FROM public.outbound_touches 
            ORDER BY ts DESC LIMIT 50
        """)
        rows = cur.fetchall()
        for r in rows:
            print(f"{r[0]} | {r[1]:8} | {r[2]:12} | {r[3][:20]:20} | {r[4]}")
            
        print("\n--- OUTREACH STATUS SUMMARY (24H) ---")
        cur.execute("""
            SELECT status, count(*) 
            FROM public.outbound_touches 
            WHERE ts > NOW() - INTERVAL '24 hours' 
            GROUP BY status
        """)
        stats = cur.fetchall()
        for s in stats:
            print(f"{s[0]:15}: {s[1]}")
            
        cur.execute("""
            SELECT count(DISTINCT company) 
            FROM public.outbound_touches 
            WHERE ts > NOW() - INTERVAL '24 hours'
        """)
        unique_companies = cur.fetchone()[0]
        print(f"\nUnique Companies Contacted (24h): {unique_companies}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_outreach()
