import os
import sys
from dotenv import load_dotenv

load_dotenv('.env')
load_dotenv('.env.local')

try:
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
except Exception:
    from supabase import create_client
    sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY'))

with open('outreach_diag_clean.log', 'w', encoding='utf-8') as f:
    f.write("=== OUTREACH DIAGNOSTICS ===\n")

    # 1. Touches in last 24h
    res = sb.table('outbound_touches').select('id', count='exact').gte('ts', '2026-02-20T00:00:00').execute()
    count = getattr(res, 'count', len(getattr(res, 'data', [])))
    f.write(f'OUTBOUND 24H: {count}\n')

    # 2. Latest touch
    last = sb.table('outbound_touches').select('ts,channel,status,phone,company').order('ts', desc=True).limit(5).execute()
    f.write('LATEST TOUCHES:\n')
    for row in getattr(last, 'data', []):
        f.write(f"  - {row.get('ts')} | {row.get('channel')} | {row.get('status')} | {row.get('company')} | {row.get('phone')}\n")

    # 3. Campaign Mode
    cm = sb.table('system_state').select('status').eq('key', 'campaign_mode').execute()
    f.write(f"CAMPAIGN MODE: {getattr(cm, 'data', [{}])[0].get('status', 'NOT FOUND')}\n")

    # 4. Eligible Leads
    leads = sb.table('contacts_master').select('id', count='exact').in_('status', ['new', 'research_done']).execute()
    leads_count = getattr(leads, 'count', len(getattr(leads, 'data', [])))
    f.write(f'ELIGIBLE LEADS: {leads_count}\n')

    # 5. Heartbeat
    hb = sb.table('system_health_log').select('checked_at,status').order('checked_at', desc=True).limit(1).execute()
    f.write(f"LAST HEARTBEAT: {getattr(hb, 'data', [{}])[0].get('checked_at', 'NONE')}\n")