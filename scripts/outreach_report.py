import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
from modules.database.supabase_client import get_supabase

load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

def get_outreach_list():
    sb = get_supabase()
    print("📋 EMPIRE OUTREACH AUDIT\n" + "="*50)
    
    dan_phone = "+13529368152"
    
    # 1. Check Dan's Memory Record Specifically
    print(f"\n🧠 CHECKING MEMORY FOR: {dan_phone}")
    try:
        mem = sb.table("customer_memory").select("*").eq("phone_number", dan_phone).execute()
        if mem.data:
            rec = mem.data[0]
            print(f" - Found Name: {rec.get('customer_name')}")
            print(f" - Context: {rec.get('context_summary')}")
        else:
            print(f" ❌ No memory record found for {dan_phone}")
    except Exception as e:
        print(f" ❌ Memory Check Error: {e}")

    # 2. Query outbound_touches
    print("\n📡 RECENT TOUCHES (outbound_touches):")
    try:
        res = sb.table("outbound_touches").select("*").order("ts", desc=True).limit(50).execute()
        if res.data:
            for row in res.data:
                print(f" - {row.get('ts')[:16]} | {row.get('channel'):<5} | {row.get('phone'):<15} | {row.get('status')}")
        else:
            print(" ⚠️ outbound_touches is empty.")
    except Exception as e:
        print(f" ❌ outbound_touches Error: {e}")

    # 3. Fallback: Check contacts_master status
    print("\n📂 CONTACTS MARKED AS CONTACTED (contacts_master):")
    try:
        res = sb.table("contacts_master").select("full_name, email, phone, status, updated_at")\
            .in_("status", ["outreach_sent", "outreach_dispatched", "calling_initiated"]).order("updated_at", desc=True).execute()
        
        if res.data:
            for row in res.data:
                name = row.get('full_name') or row.get('email') or 'Unknown'
                print(f" - {row.get('updated_at')[:16]} | {row.get('status'):<20} | {name:<25} | {row.get('phone')}")
        else:
            print(" ⚠️ No leads marked as contacted in contacts_master.")
    except Exception as e:
        print(f" ❌ contacts_master Audit Error: {e}")

if __name__ == "__main__":
    get_outreach_list()
