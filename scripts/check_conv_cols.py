"""Check conversation_logs actual columns"""
import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(url, key)

# Get conversation_logs columns by fetching one row 
r = sb.table("conversation_logs").select("*").limit(1).execute()
if r.data:
    print("COLUMNS:", list(r.data[0].keys()))
    print("SAMPLE:", {k: str(v)[:50] if v else None for k, v in r.data[0].items()})
else:
    print("Table empty - trying RPC")
    # List recent from any phone
    r2 = sb.table("conversation_logs").select("*").limit(3).execute()
    print("Rows:", r2.data)
