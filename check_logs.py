from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
import datetime

sb = get_supabase()
logs = sb.table('brain_logs').select('message, timestamp').order('timestamp', desc=True).limit(20).execute()
for l in logs.data:
    print(f"[{l['timestamp']}] {l['message']}")
