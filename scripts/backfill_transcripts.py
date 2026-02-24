import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env')
load_dotenv('.env.local')

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
sb = create_client(url, key)

print("Fetching historical transcripts from system health logs...")
logs = sb.table('system_health_log').select('*').eq('check_type', 'call_alert').order('checked_at', desc=True).limit(100).execute()
print(f"Found {len(logs.data)} call records.")

updates = 0
for lg in logs.data:
    details = lg.get('details', {})
    phone = details.get('caller_phone')
    transcript = details.get('transcript', '')
    
    if phone and transcript:
        touches = sb.table('outbound_touches').select('id, body').eq('phone', phone).eq('channel', 'call').execute()
        for t in touches.data:
            if not t.get('body'):
                sb.table('outbound_touches').update({
                    'body': transcript[-10000:], 
                    'status': 'completed'
                }).eq('id', t['id']).execute()
                print(f"✅ Backfilled transcript for {phone}")
                updates += 1

print(f"Backfill complete! Fixed {updates} dashboard entries.")
