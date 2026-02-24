import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from modules.database.supabase_client import get_supabase

def check_traces():
    sb = get_supabase()
    
    print("Fetching system_health_log for 'heartbeat_v3' errors...")
    res = sb.table('system_health_log').select('*').eq('check_type', 'heartbeat_v3').in_('status', ['degraded', 'error']).order('checked_at', desc=True).limit(5).execute()
    
    if not res.data:
        print("No bounces recorded yet. Waiting for next cron pulse...")
    else:
        for log in res.data:
            print(f"[{log['checked_at']}] {log['status']}")
            print(f"   Trace: {log.get('details', {}).get('error', 'N/A')}")
            
if __name__ == "__main__":
    check_traces()
