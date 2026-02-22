import os
import json
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
from datetime import datetime, timezone

def test():
    sb = get_supabase()
    
    try:
        res1 = sb.table("system_state").upsert({
            "key": "test_key",
            "status": "working",
            "last_error": "none",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }, on_conflict="key").execute()
        print("State OK", res1)
    except Exception as e:
        print("State ERROR:", getattr(e, 'message', str(e)), getattr(e, 'details', ''))

    try:
        res2 = sb.table("system_health_log").insert({
            "status": "tuning_complete",
            "details": json.dumps({"test": 123})
        }).execute()
        print("Health OK", res2)
    except Exception as e:
        print("Health ERROR:", getattr(e, 'message', str(e)), getattr(e, 'details', ''))

if __name__ == '__main__':
    test()
