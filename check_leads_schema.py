from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

def check_schema():
    sb = get_supabase()
    res = sb.table("leads").select("*").limit(1).execute()
    if res.data:
        print("Columns in 'leads':")
        for col in res.data[0].keys():
            print(f"  - {col}")
    else:
        print("No data in 'leads' table.")

if __name__ == "__main__":
    check_schema()
