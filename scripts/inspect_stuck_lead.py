import os, psycopg2, json
from dotenv import load_dotenv

load_dotenv()

def inspect_stuck_leads():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, company_name, status, raw_research, website_url 
            FROM public.contacts_master 
            WHERE status = 'new' AND raw_research IS NOT NULL 
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            print("No stuck leads found.")
            return
            
        print(f"ID: {row[0]}")
        print(f"Company: {row[1]}")
        print(f"Status: {row[2]}")
        print(f"URL: {row[4]}")
        print(f"Raw Research Preview: {json.dumps(row[3], indent=2)[:500]}...")
        
        # Check if this ID exists in audit_reports
        cur.execute("SELECT count(*) FROM public.audit_reports WHERE lead_id = %s", (row[0],))
        print(f"Exists in audit_reports: {cur.fetchone()[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_stuck_leads()
