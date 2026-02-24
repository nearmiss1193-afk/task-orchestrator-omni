import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from modules.database.supabase_client import get_supabase

def check():
    sb = get_supabase()
    
    # 1. Total counts
    res = sb.table('contacts_master').select('status').execute()
    from collections import Counter
    counts = Counter([r['status'] for r in res.data])
    print("CURRENT PIPELINE COUNTS:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
        
    print("\n")
        
    # 2. Check recent delivery_failed
    res_failed = sb.table('contacts_master').select('id, email, company_name, notes').eq('status', 'delivery_failed').limit(5).execute()
    print("SAMPLE DELIVERY FAILED LEADS:")
    for l in res_failed.data:
        print(f" - {l['id']}: {l['email']} ({l['company_name']})")
        print(f"   NOTES: {l.get('notes')}")
        
    # 3. Check outbound_touches in last hour
    try:
        from datetime import datetime, timezone, timedelta
        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        touches = sb.table('outbound_touches').select('company, channel, status').gte('ts', one_hour_ago).execute()
        print("\nTOUCHES IN LAST HOUR:", len(touches.data))
        for t in touches.data[:5]:
            print(f" - {t['channel']} to {t['company']} ({t['status']})")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check()
