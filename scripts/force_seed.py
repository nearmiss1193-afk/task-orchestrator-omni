import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
from modules.database.supabase_client import get_supabase

load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

def force_seed():
    sb = get_supabase()
    phone = "+13529368152"
    print(f"🛠️ FORCING SEED FOR: {phone}")
    
    # Check if exists
    res = sb.table("customer_memory").select("*").eq("phone_number", phone).execute()
    
    data = {
        "customer_name": "Dan",
        "context_summary": {
            "contact_name": "Dan",
            "history": "Verified by Antigravity.",
            "status": "Priority Test"
        },
        "status": "active"
    }
    
    if res.data:
        print(" -> Record exists. Updating...")
        update_res = sb.table("customer_memory").update(data).eq("phone_number", phone).execute()
        print(f" ✅ Update: {update_res.data}")
    else:
        print(" -> Creating new record...")
        data["phone_number"] = phone
        insert_res = sb.table("customer_memory").insert(data).execute()
        print(f" ✅ Insert: {insert_res.data}")

if __name__ == "__main__":
    force_seed()
