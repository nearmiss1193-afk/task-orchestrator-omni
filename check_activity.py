"""Check call and campaign activity"""
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

print("=" * 60)
print("CALL & CAMPAIGN ACTIVITY CHECK")
print(f"Time: {datetime.now().isoformat()}")
print("=" * 60)

# Check recent system logs
print("\n=== RECENT SYSTEM LOGS ===")
result = client.table('system_logs').select('*').order('created_at', desc=True).limit(20).execute()
for log in result.data:
    ts = log.get('created_at', 'N/A')[:16] if log.get('created_at') else 'N/A'
    msg = log.get('message', log.get('event_type', 'N/A'))
    print(f"{ts}: {str(msg)[:80]}")

# Check for OUTREACH specifically
print("\n=== CLOUD_OUTREACH EVENTS (last 3 days) ===")
three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
result = client.table('system_logs').select('*').gte('created_at', three_days_ago).execute()
outreach = [r for r in result.data if 'OUTREACH' in str(r.get('message', '')) or 'OUTREACH' in str(r.get('event_type', ''))]
for log in outreach[-10:]:
    ts = log.get('created_at', 'N/A')[:16]
    meta = log.get('metadata', {})
    print(f"{ts}: {log.get('message', 'N/A')}")
    if meta:
        print(f"   → {meta}")

# Check leads status
print("\n=== LEADS BY STATUS ===")
for status in ['new', 'processing_email', 'called', 'contacted', 'qualified']:
    result = client.table('leads').select('id', count='exact').eq('status', status).execute()
    count = result.count if result.count is not None else len(result.data)
    print(f"  {status}: {count}")

# Check call_transcripts
print("\n=== RECENT CALL TRANSCRIPTS ===")
calls = client.table('call_transcripts').select('*').order('created_at', desc=True).limit(5).execute()
if calls.data:
    for call in calls.data:
        ts = call.get('created_at', 'N/A')[:16] if call.get('created_at') else 'N/A'
        phone = call.get('phone_number', 'N/A')
        print(f"{ts}: {phone}")
else:
    print("  No call transcripts found!")

# Check call_logs
print("\n=== RECENT CALL LOGS ===")
try:
    calls = client.table('call_logs').select('*').order('created_at', desc=True).limit(5).execute()
    if calls.data:
        for call in calls.data:
            ts = call.get('created_at', 'N/A')[:16] if call.get('created_at') else 'N/A'
            phone = call.get('phone_number', 'N/A')
            status = call.get('status', 'N/A')
            print(f"{ts}: {phone} - {status}")
    else:
        print("  No call logs found!")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
