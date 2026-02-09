import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
from modules.database.supabase_client import get_supabase

load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

def deep_audit():
    sb = get_supabase()
    print("📋 DEEP OUTREACH AUDIT\n" + "="*50)
    
    statuses = ["outreach_sent", "outreach_dispatched", "calling_initiated", "contacted"]
    
    try:
        res = sb.table("contacts_master").select("full_name, email, phone, status, updated_at")\
            .in_("status", statuses).order("updated_at", desc=True).execute()
        
        if res.data:
            print(f"{'STATUS':<20} | {'NAME':<25} | {'CONTACT':<30}")
            print("-" * 80)
            for row in res.data:
                name = row.get('full_name') or 'N/A'
                contact = row.get('email') or row.get('phone') or 'N/A'
                print(f"{row.get('status'):<20} | {name:<25} | {contact:<30}")
        else:
            print(" ⚠️ No Leads found with outreach statuses.")
            
        print("\n📊 ALL STATUS COUNTS:")
        all_res = sb.table("contacts_master").select("status").execute()
        from collections import Counter
        counts = Counter([r['status'] for r in all_res.data])
        for s, c in counts.items():
            print(f" - {s}: {c}")
            
    except Exception as e:
        print(f" ❌ Total Audit Error: {e}")

if __name__ == "__main__":
    deep_audit()
