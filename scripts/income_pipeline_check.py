import os
from datetime import datetime, timedelta, timezone
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('apps/portal/.env.local')
supabase = create_client(os.environ.get('NEXT_PUBLIC_SUPABASE_URL'), os.environ.get('SUPABASE_SERVICE_ROLE_KEY'))

now = datetime.now(timezone.utc)
last_24h = (now - timedelta(hours=24)).isoformat()
last_7d = (now - timedelta(days=7)).isoformat()

def run_check():
    try:
        sent_res = supabase.table('outbound_touches').select('id', count='exact').gt('ts', last_24h).execute()
        sent_count = sent_res.count if sent_res else 0
        
        open_count = "N/A"
        try:
            open_res = supabase.table('outbound_touches').select('id', count='exact').eq('opened', True).gt('ts', last_7d).execute()
            open_count = open_res.count if open_res else 0
        except: pass

        reply_count = "N/A"
        try:
            reply_res = supabase.table('outbound_touches').select('id', count='exact').eq('status', 'replied').gt('ts', last_7d).execute()
            reply_count = reply_res.count if reply_res else 0
        except: pass

        pipe_res = supabase.table('contacts_master').select('id', count='exact').in_('status', ['new', 'research_done']).execute()
        pipe_count = pipe_res.count if pipe_res else 0

        with open("income.txt", "w", encoding="utf-8") as f:
            f.write("┌────────────────────────────────────────┐\n")
            f.write(f"│ INCOME PIPELINE — {now.strftime('%Y-%m-%d')}           │\n")
            f.write(f"│ Sending:   {sent_count} touches in last 24h\n")
            f.write(f"│ Opening:   {open_count} opens in last 7d\n")
            f.write(f"│ Replying:  {reply_count} replies in last 7d\n")
            f.write(f"│ Booking:   X appointments this week    │\n")
            f.write(f"│ Paying:    X payments this week        │\n")
            f.write(f"│ Pipeline:  {pipe_count} contactable leads remain\n")
            f.write("└────────────────────────────────────────┘\n")
            
    except Exception as e:
        with open("income.txt", "w") as f:
            f.write(f"Error: {e}")

if __name__ == "__main__":
    run_check()
