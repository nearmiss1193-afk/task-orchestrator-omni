import os, psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_leads():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # 1. New leads with website_url
        cur.execute("SELECT count(*) FROM public.contacts_master WHERE status = 'new' AND website_url IS NOT NULL")
        new_with_url = cur.fetchone()[0]
        
        # 2. Total research_done
        cur.execute("SELECT count(*) FROM public.contacts_master WHERE status = 'research_done'")
        research_done = cur.fetchone()[0]
        
        # 3. Total new
        cur.execute("SELECT count(*) FROM public.contacts_master WHERE status = 'new'")
        new_total = cur.fetchone()[0]
        
        print(f"Total Leads (Status: 'new'): {new_total}")
        print(f"Leads (Status: 'new') with website_url: {new_with_url}")
        print(f"Total Research Done: {research_done}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_leads()
