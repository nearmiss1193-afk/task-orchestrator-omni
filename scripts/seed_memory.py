import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
from modules.database.supabase_client import get_supabase

load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

phone = "+13529368152"

def seed_memory():
    sb = get_supabase()
    print(f"🌱 Seeding Memory for: {phone}")
    
    # 1. Update customer_memory
    ctx = {
        "contact_name": "Dan",
        "history": "[System]: Manual seed for Perfect Memory test.",
        "business": "AI Services",
        "challenge": "Vapi memory persistence"
    }
    
    res = sb.table("customer_memory").update({
        "customer_name": "Dan",
        "context_summary": ctx
    }).eq("phone_number", phone).execute()
    
    if res.data:
        print("✅ Seed successful.")
        print(f"📊 New Record: {res.data[0]}")
    else:
        print("❌ Seed failed.")

if __name__ == "__main__":
    seed_memory()
