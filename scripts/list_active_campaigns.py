import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from modules.database.supabase_client import get_supabase

def list_campaigns():
    sb = get_supabase()
    
    # 1. Check system_state for explicit toggles
    res = sb.table('system_state').select('key, status').execute()
    states = res.data or []
    print("--- SYSTEM STATE TOGGLES ---")
    for s in states:
        print(f"{s['key']}: {s.get('status', 'N/A')}")
        
    print("\n--- OUTBOUND TOUCHES (Last 2 hours) ---")
    from datetime import datetime, timezone, timedelta
    two_hours_ago = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    touches = sb.table('outbound_touches').select('channel, variant_name, status').gte('ts', two_hours_ago).execute()
    from collections import Counter
    if touches.data:
        channels = Counter([t.get('channel') for t in touches.data])
        variants = Counter([t.get('variant_name', 'Unknown') for t in touches.data])
        statuses = Counter([t.get('status') for t in touches.data])
        print("Channels:", dict(channels))
        print("Statuses:", dict(statuses))
        print("Recent Variants/Campaigns:")
        for k, v in variants.items():
            print(f" - {k}: {v} touches")
    else:
        print("No touches in the last 2 hours. The queue might still be processing the new unblocked batch.")

if __name__ == "__main__":
    list_campaigns()
