import os
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

def dump_schema():
    sb = get_supabase()
    tables = ["outbound_touches", "conversation_logs", "system_health_log", "system_state"]
    for table in tables:
        print(f"\n--- TABLE: {table} ---")
        try:
            # We can't easily get the schema via the client, but we can look at one row's keys
            res = sb.table(table).select("*").limit(1).execute()
            if res.data:
                print("Columns:", list(res.data[0].keys()))
                print("Sample Row:", res.data[0])
            else:
                print("Table is empty (no keys found)")
        except Exception as e:
            print(f"Error reading {table}: {e}")

if __name__ == "__main__":
    dump_schema()
