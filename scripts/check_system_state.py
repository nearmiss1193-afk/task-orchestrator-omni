from modules.database.supabase_client import get_supabase

def check_system_state():
    sb = get_supabase()
    print("--- TABLE: system_state ---")
    try:
        res = sb.table("system_state").select("*").limit(1).execute()
        if res.data:
            print("Columns:", list(res.data[0].keys()))
            print("Sample Row:", res.data[0])
        else:
            print("Table is empty")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_system_state()
