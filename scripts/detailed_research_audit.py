import os, psycopg2, json
from dotenv import load_dotenv

load_dotenv()

def audit_research():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # 1. Total leads by status
        print("--- LEAD STATUS SUMMARY ---")
        cur.execute("SELECT status, count(*) FROM public.contacts_master GROUP BY status")
        [print(f"  {r[0]:15}: {r[1]}") for r in cur.fetchall()]
        
        # 2. Check for leads with status='new' but having website_url
        cur.execute("SELECT count(*) FROM public.contacts_master WHERE status = 'new' AND website_url IS NOT NULL")
        print(f"\nEligible for Research ('new' + URL): {cur.fetchone()[0]}")
        
        # 3. Check for recent successful audits
        print("\n--- RECENT SUCCESSFUL AUDITS (audit_reports) ---")
        cur.execute("SELECT created_at, company_name, report_id FROM public.audit_reports ORDER BY created_at DESC LIMIT 5")
        rows = cur.fetchall()
        if not rows:
            print("  No audits found in audit_reports table.")
        for r in rows:
            print(f"  {r[0]} | {r[1][:25]:25} | {r[2]}")
            
        # 4. Check for leads that might be 'stuck' (e.g. have raw_research but still status='new')
        cur.execute("SELECT count(*) FROM public.contacts_master WHERE status = 'new' AND raw_research IS NOT NULL")
        print(f"\nLeads with status='new' but have raw_research: {cur.fetchone()[0]}")
        
        # 5. Check for system health alerts related to research
        print("\n--- RECENT RESEARCH ALERTS ---")
        cur.execute("SELECT checked_at, details FROM public.system_health_log WHERE details::text ILIKE '%research%' OR details::text ILIKE '%pagespeed%' ORDER BY checked_at DESC LIMIT 5")
        [print(f"  {r[0]} | {r[1]}") for r in cur.fetchall()]
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_research()
