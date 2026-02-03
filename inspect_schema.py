
import os
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

def inspect_schema():
    supabase = get_supabase()
    if not supabase:
        return

    print("🔍 Inspecting 'system_state' table...")
    try:
        # Querying an item to see what columns come back
        res = supabase.table("system_state").select("*").limit(1).execute()
        if res.data:
            print(f"Columns found: {list(res.data[0].keys())}")
        else:
            print("Table empty or no data.")
    except Exception as e:
        print(f"Error inspecting: {e}")

if __name__ == "__main__":
    inspect_schema()
