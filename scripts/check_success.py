import os, sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
sb = get_supabase()
res = sb.table('outbound_touches').select('ts', 'channel', 'status', 'payload').order('ts', desc=True).limit(5).execute()
if res.data:
    for r in res.data:
        provider = r.get('payload', {}).get('provider', 'unknown') if r.get('payload') else 'unknown'
        print(f"{r.get('ts')} | {r.get('channel')} | {r.get('status')} | {provider}")
else:
    print("No recent touches.")
