import os
from supabase import create_client

# Hardcoded from .env for immediate debug reliability
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def check_status():
    print("Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Total Counts by Status
    print("\n--- Lead Status Counts ---")
    try:
        # Fetch all status fields
        res = supabase.table('leads').select('status').execute()
        counts = {}
        for row in res.data:
            s = row.get('status', 'UNION')
            counts[s] = counts.get(s, 0) + 1
        
        for status, count in counts.items():
            print(f"{status}: {count}")
    except Exception as e:
        print(f"Error fetching counts: {e}")

    # 2. Check "Reservations" (converted / appointment_set)
    print("\n--- 'Reservations' Details ---")
    try:
        res = supabase.table('leads').select('*').in_('status', ['converted', 'appointment_set']).execute()
        if not res.data:
            print("No leads found with status 'converted' or 'appointment_set'.")
            # Fallback: Maybe logic uses 'qualified'?
            res = supabase.table('leads').select('*').eq('status', 'qualified').execute()
            if res.data:
                print(f"Found {len(res.data)} 'qualified' leads (maybe these are them?):")
        
        for lead in res.data:
            print(f"- {lead.get('company_name')} ({lead.get('status')}): {lead.get('notes')}")
            
    except Exception as e:
        print(f"Error fetching reservations: {e}")

    # 3. Check Transcripts
    print("\n--- Call Transcripts ---")
    try:
        res = supabase.table('call_transcripts').select('*', count='exact').execute()
        print(f"Total Call Transcripts: {len(res.data)}")
        if res.data:
            print("Last 3 transcripts:")
            for t in res.data[:3]:
                 print(f"- {t.get('created_at')} | {t.get('summary')[:50]}...")
    except Exception as e:
        print(f"Error fetching transcripts: {e}")

if __name__ == "__main__":
    check_status()
