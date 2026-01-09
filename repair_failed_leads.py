# repair_failed_leads.py - Reset status to retry
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def main():
    s = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get all failed leads that have phone in agent_research
    failed = s.table('leads').select('*').eq('status', 'failed_init').execute().data
    
    can_repair = []
    no_phone = []
    
    for lead in failed:
        research = lead.get('agent_research') or {}
        if isinstance(research, dict) and research.get('phone'):
            can_repair.append(lead['id'])
        else:
            no_phone.append(lead.get('company_name', 'Unknown'))
    
    print(f"Can repair (have phone): {len(can_repair)}")
    print(f"No phone in research: {len(no_phone)}")
    
    if can_repair:
        # Batch update - reset to ready_to_send
        for lid in can_repair:
            s.table('leads').update({'status': 'ready_to_send'}).eq('id', lid).execute()
        print(f"DONE: Reset {len(can_repair)} leads to 'ready_to_send'")
    
    if no_phone:
        print(f"Cannot repair (no phone): {no_phone[:5]}...")

if __name__ == "__main__":
    main()
