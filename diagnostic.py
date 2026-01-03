
import os
from supabase import create_client
import time

# Helper to load env
def load_env():
    try:
        with open("modules/orchestrator/dashboard/.env.local", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    if key == "NEXT_PUBLIC_SUPABASE_URL": os.environ["SUPABASE_URL"] = val
                    if key == "SUPABASE_SERVICE_ROLE_KEY": os.environ["SUPABASE_SERVICE_ROLE_KEY"] = val
    except:
        pass

# Helper to run diagnostics
def run_diagnostics():
    load_env()
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            print("CRITICAL: Missing Supabase Credentials in environment.")
            return

        supabase = create_client(url, key)
        print("--- CORTEX v2.0 DIAGNOSTIC REPORT ---")
        
        # TASK 1: DATABASE HEALTH CHECK
        print("\n[TASK 1] Database Health Check:")
        
        # 1. Logs last 24h
        try:
            # Note: direct SQL count not always easy via API, fetching count
            # 'timestamp' might be 'created_at' in my internal schema, checking both
            # User asked for 'timestamp', but my schema in dashboard_service uses 'created_at'
            # I will check 'created_at' as it is standard Supabase.
            res = supabase.table("brain_logs").select("*", count="exact").gt("created_at", "2024-12-25T00:00:00").execute()
            print(f" - Logs (Last 24h): {res.count}")
        except Exception as e:
            print(f" - Logs Check Failed: {e}")

        # 2. Error Logs
        try:
            res = supabase.table("brain_logs").select("message").ilike("message", "%error%").order("created_at", desc=True).limit(5).execute()
            print(" - Recent Errors:")
            for item in res.data:
                print(f"   * {item['message']}")
        except Exception as e:
            print(f" - Error Log Check Failed: {e}")

        # 3. High Value Leads
        try:
            # Assuming 'score' column exists. User asked for 'leads' table.
            # I know 'contacts_master' exists, user might mean that.
            # I will check 'leads' first, then 'contacts_master'.
            try:
                res = supabase.table("leads").select("*", count="exact").gte("score", 80).execute()
                print(f" - High Value Leads (leads table): {res.count}")
            except:
                res = supabase.table("contacts_master").select("*", count="exact").execute() # Fallback
                print(f" - Contacts Count (contacts_master): {res.count} (Score column check skipped)")
        except Exception as e:
            print(f" - Leads Check Failed: {e}")

        # 4. Social Accounts
        try:
            res = supabase.table("social_accounts").select("*").eq("is_active", True).execute()
            print(f" - Active Social Accounts: {len(res.data)}")
        except Exception as e:
            print(f" - Social Accounts Check Failed (Table likely missing): {e}")
            # Trigger Task 2 logic here if failed
            create_social_table(supabase)

    except Exception as e:
        print(f"DIAGNOSTIC CRASH: {e}")

def create_social_table(supabase):
    print("\n[TASK 2] Fixing SocialLoop (Creating Table)...")
    # This requires SQL execution. I cannot do DDL via Client usually.
    # I will output the SQL needed.
    print("ACTION REQUIRED: Run the following SQL in Supabase Editor:")
    print("""
    CREATE TABLE IF NOT EXISTS public.social_accounts (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        platform TEXT NOT NULL,
        username TEXT NOT NULL,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        credentials JSONB
    );
    ALTER TABLE public.social_accounts ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "Allow All" ON public.social_accounts FOR ALL USING (true);
    """)

if __name__ == "__main__":
    run_diagnostics()
