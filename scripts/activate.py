import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')

sb = create_client(url, key)

try:
    res = sb.table('system_state').update({'status': 'working'}).eq('key', 'campaign_mode').execute()
    print("✅ Campaign mode successfully flipped to:", res.data[0]['status'] if res.data else 'Unknown')
except Exception as e:
    print("❌ Failed to update campaign mode:", e)
