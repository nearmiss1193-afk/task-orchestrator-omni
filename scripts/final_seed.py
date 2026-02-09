import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
from modules.database.supabase_client import get_supabase

load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

phone = "+13529368152"

def final_seed():
    sb = get_supabase()
    print(f"🌱 Final Seed for: {phone}")
    
    # Try a simple update of the name first
    try:
        res = sb.table("customer_memory").update({
            "customer_name": "Dan",
            "context_summary": {
                "contact_name": "Dan",
                "history": "[System]: Verified memory bridge active.",
                "business": "AI Service Co"
            }
        }).eq("phone_number", phone).execute()
        
        if res.data:
            print(f"✅ Success! Named saved: {res.data[0].get('customer_name')}")
        else:
            print("⚠️ No record found to update. Attempting insert...")
            res_ins = sb.table("customer_memory").insert({
                "phone_number": phone,
                "customer_name": "Dan",
                "context_summary": {"contact_name": "Dan", "history": "New"},
                "status": "active"
            }).execute()
            print(f"✅ Insert result: {res_ins.data}")
    except Exception as e:
        print(f"❌ Final Seed Error: {e}")

if __name__ == "__main__":
    final_seed()
