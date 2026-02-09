import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
from modules.database.supabase_client import get_supabase

load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

def final_audit_report():
    sb = get_supabase()
    output_file = "outreach_list.txt"
    
    with open(output_file, "w") as f:
        f.write("📋 EMPIRE ONBOARDING AUDIT - " + os.popen("date /t").read() + "\n")
        f.write("="*50 + "\n\n")
        
        try:
            # 1. Status Summary
            f.write("📊 SYSTEM STATUS SUMMARY:\n")
            res = sb.table("contacts_master").select("status").execute()
            from collections import Counter
            counts = Counter([r['status'] for r in res.data])
            for s, c in counts.items():
                f.write(f" - {s}: {c}\n")
            
            # 2. Detailed Outreach List
            f.write("\n📡 CONTACTED LEADS (SMS/Email/Voice):\n")
            f.write(f"{'STATUS':<20} | {'NAME':<25} | {'CONTACT'}\n")
            f.write("-" * 80 + "\n")
            
            target_statuses = ["outreach_sent", "outreach_dispatched", "calling_initiated", "contacted"]
            leads = sb.table("contacts_master").select("full_name, email, phone, status")\
                .in_("status", target_statuses).execute()
            
            if leads.data:
                for row in leads.data:
                    name = row.get('full_name') or 'N/A'
                    contact = row.get('email') or row.get('phone') or 'N/A'
                    f.write(f"{row.get('status'):<20} | {name:<25} | {contact}\n")
            else:
                f.write("⚠️ No leads found in 'contacted' statuses.\n")
                
            # 3. Dan's Test Sync
            f.write("\n🧠 DAN'S MEMORY SYNC (+13529368152):\n")
            mem = sb.table("customer_memory").select("*").eq("phone_number", "+13529368152").execute()
            if mem.data:
                f.write(f" - Name: {mem.data[0].get('customer_name')}\n")
                f.write(f" - Context: {mem.data[0].get('context_summary')}\n")
            else:
                f.write(" ❌ No record found.\n")

            print(f"✅ Report generated: {output_file}")
            
        except Exception as e:
            f.write(f"\n❌ Audit Failed: {e}\n")
            print(f"❌ Audit Failed: {e}")

if __name__ == "__main__":
    final_audit_report()
