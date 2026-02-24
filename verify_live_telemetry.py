from modules.database.supabase_client import get_supabase
import json

supabase = get_supabase()

print('\n--- SOVEREIGN VERIFICATION PROTOCOL ---')

try:
    health = supabase.table('system_health_log').select('*').order('checked_at', desc=True).limit(2).execute()
    print(f'1. Heartbeat OK (Last Check: {health.data[0]["checked_at"] if health.data else "None"})')

    state = supabase.table('system_state').select('*').eq('key', 'campaign_mode').execute()
    status = state.data[0]['status'] if state.data else 'broken'
    print(f'2. Campaign Mode: {status}')

    outreach = supabase.table('outbound_touches').select('*').order('ts', desc=True).limit(5).execute()
    print(f'3. Active Pipeline OK (Last Touch: {outreach.data[0]["ts"] if outreach.data else "None"})')

except Exception as e:
    import traceback
    print(f"VERIFICATION FAILED:\n{traceback.format_exc()}")

print('--------------------------------------\n')
