# get_campaign_status.py - Full campaign status check
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def main():
    with open("campaign_status.txt", "w", encoding="utf-8") as f:
        try:
            s = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Get leads
            leads = s.table('leads').select('*').execute().data
            f.write(f"=== LEADS ({len(leads)}) ===\n")
            for lead in leads:
                f.write(f"  - {lead.get('name','?')} | {lead.get('phone','?')} | Status: {lead.get('status','?')}\n")
            
            # Get transcripts
            transcripts = s.table('call_transcripts').select('*').order('created_at', desc=True).limit(10).execute().data
            f.write(f"\n=== CALL TRANSCRIPTS ({len(transcripts)}) ===\n")
            for t in transcripts:
                f.write(f"  - {t.get('created_at','?')[:19] if t.get('created_at') else '?'}\n")
                f.write(f"    Phone: {t.get('customer_number','?')}\n")
                f.write(f"    Duration: {t.get('duration','?')}s\n")
                f.write(f"    Outcome: {t.get('call_outcome','?')}\n")
                if t.get('transcript'):
                    snippet = t.get('transcript','')[:300].replace('\n',' ')
                    f.write(f"    Snippet: {snippet}...\n")
                f.write("\n")
            
            # Get system logs
            logs = s.table('system_logs').select('*').order('created_at', desc=True).limit(5).execute().data
            f.write(f"\n=== SYSTEM LOGS ({len(logs)}) ===\n")
            for log in logs:
                f.write(f"  - {log.get('created_at','?')[:19] if log.get('created_at') else '?'} | {log.get('event_type','?')} | {log.get('message','?')[:80]}\n")
            
            f.write("\n=== CAMPAIGN STATUS: COMPLETE ===\n")
            
        except Exception as e:
            f.write(f"ERROR: {e}\n")

if __name__ == "__main__":
    main()
    print("Status written to campaign_status.txt")
