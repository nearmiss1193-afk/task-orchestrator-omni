from modules.database.supabase_client import get_supabase
import json

def check_schema():
    sb = get_supabase()
    res = sb.table("contacts_master").select("*").limit(1).execute()
    if res.data:
        print(f"Columns: {list(res.data[0].keys())}")
    else:
        print("No data found in contacts_master")

if __name__ == "__main__":
    check_schema()
