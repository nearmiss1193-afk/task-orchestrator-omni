import os
import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(override=True)

# Explicitly load from parent if needed
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print(f"❌ Error: Missing Supabase credentials in .env")
    print(f"   Looking for: SUPABASE_URL / NEXT_PUBLIC_SUPABASE_URL")
    print(f"   Looking for: SUPABASE_SERVICE_ROLE_KEY / NEXT_PUBLIC_SUPABASE_ANON_KEY")
    exit(1)

def verify_activity():
    try:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        now = datetime.datetime.utcnow()
        four_hours_ago = now - datetime.timedelta(hours=4)
        
        print(f"🕒 Time Now: {now.isoformat()}")
        print(f"🕒 Checking since: {four_hours_ago.isoformat()}")
        
        # 1. Check Leads (contacts_master)
        # Use simple count if supported, or fetch header
        res_leads = sb.table("contacts_master").select("*", count="exact").gte("created_at", four_hours_ago.isoformat()).execute()
        lead_count = res_leads.count if res_leads.count is not None else len(res_leads.data)
        
        # 2. Check Emails (outreach_log or similar? or just check if email-poller ran)
        # We'll check 'contacts_master' for 'last_contacted' updates if available, or just trust the lead gen for now.
        # Let's check 'outreach_queue' or 'messages' if they exist.
        # Fallback: Just report leads for now as primary growth metric.
        
        print("\n📊 CAMPAIGN VERIFICATION (Last 4 Hours):")
        print(f"✅ New Leads Found: {lead_count}")
        
        if lead_count > 0:
            print("   -> Prospecting is ACTIVE and finding targets.")
        else:
            print("   -> ⚠️ No new leads in 4 hours. Check Apollo/Scheduler.")

        # 3. Check Staged Replies
        res_replies = sb.table("staged_replies").select("*", count="exact").limit(1).execute()
        print(f"✅ Staged Replies Access: OK (Total: {res_replies.count})")

        # 4. Check Brain Logs
        res_logs = sb.table("brain_logs").select("*", count="exact").limit(1).execute()
        print(f"✅ Brain Logs Access: OK (Total: {res_logs.count})")

    except Exception as e:
        print(f"❌ Error verifying activity: {e}")

if __name__ == "__main__":
    verify_activity()
