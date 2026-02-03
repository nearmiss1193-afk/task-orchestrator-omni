from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

def check_leads():
    sb = get_supabase()
    res = sb.table("leads").select("id", count="exact").limit(1).execute()
    print(f"📦 Total Leads in 'leads' table: {res.count}")
    
    if res.count > 0:
        statuses = sb.table("leads").select("status").execute()
        from collections import Counter
        counts = Counter([r['status'] for r in statuses.data])
        print(f"📊 Lead Statuses: {dict(counts)}")

if __name__ == "__main__":
    check_leads()
