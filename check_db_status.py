
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"DEBUG: URL found? {bool(url)}")
print(f"DEBUG: KEY found? {bool(key)}")

if url and key:
    try:
        s = create_client(url, key)
        
        # Leads
        try:
            res = s.table('leads').select('*', count='exact', head=True).execute()
            print(f"DATA: Leads Count = {res.count}")
        except Exception as e:
            print(f"ERROR: Leads table check failed: {e}")

        # Transcripts
        try:
            res = s.table('call_transcripts').select('*', count='exact', head=True).execute()
            print(f"DATA: call_transcripts Count = {res.count}")
        except Exception as e:
            print(f"ERROR: call_transcripts table check failed: {e}")

        # Logs
        try:
            res = s.table('system_logs').select('*', count='exact', head=True).execute()
            print(f"DATA: system_logs Count = {res.count}")
        except Exception as e:
            print(f"ERROR: system_logs table check failed: {e}")
            
    except Exception as e:
        print(f"CRITICAL: Client init failed: {e}")
else:
    print("CRITICAL: Missing credentials in .env")
