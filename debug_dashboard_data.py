
import os
from dotenv import load_dotenv
from supabase import create_client
import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ No Supabase Creds")
    exit()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def count_table(table):
    try:
        res = supabase.table(table).select('*', count='exact').execute()
        return len(res.data)
    except Exception as e:
        return f"Error: {e}"

    with open("dashboard_data_utf8.txt", "w", encoding="utf-8") as f:
        f.write(f"--- DATABASE DIAGNOSTIC ({datetime.datetime.now()}) ---\n")
        f.write(f"Leads Total: {count_table('leads')}\n")
        f.write(f"Transcripts: {count_table('call_transcripts')}\n")
        f.write(f"System Logs: {count_table('system_logs')}\n")
        
        # Check recent logs
        try:
            res = supabase.table('system_logs').select('*').order('created_at', desc=True).limit(5).execute()
            f.write("\nRecent Logs:\n")
            for log in res.data:
                f.write(f"- {log.get('created_at')}: {log.get('event')} - {log.get('details')}\n")
        except:
            f.write("No logs found.\n")
            
        # Check recent calls
        try:
            res = supabase.table('call_transcripts').select('*').order('created_at', desc=True).limit(5).execute()
            f.write("\nRecent Calls:\n")
            for call in res.data:
                f.write(f"- {call.get('created_at')}: {call.get('summary')}\n")
        except:
            f.write("No calls found.\n")
            
    print("✅ Diagnostic written to dashboard_data_utf8.txt")
