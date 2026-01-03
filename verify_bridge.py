import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

print("🔍 Testing Autonomous Bridge (RPC: exec_sql)...")

try:
    # 1. Create Identity Verification Table
    sql_create = "CREATE TABLE IF NOT EXISTS public.agent_identity_card (id text PRIMARY KEY, status text);"
    supabase.rpc("exec_sql", {"query": sql_create}).execute()
    print("✅ Step 1: CREATE TABLE success.")
    
    # 2. Insert Agent Signature
    sql_insert = "INSERT INTO public.agent_identity_card (id, status) VALUES ('agent_007', 'LICENSE_TO_KILL_BUGS') ON CONFLICT DO NOTHING;"
    supabase.rpc("exec_sql", {"query": sql_insert}).execute()
    print("✅ Step 2: INSERT success.")
    
    # 3. Verify Data
    res = supabase.table("agent_identity_card").select("*").eq("id", "agent_007").execute()
    if res.data and res.data[0]['status'] == 'LICENSE_TO_KILL_BUGS':
         print("✅ Step 3: SELECT verification success.")
    else:
         print("❌ Step 3: SELECT failed.")
         
    # 4. Clean Up
    sql_drop = "DROP TABLE public.agent_identity_card;"
    supabase.rpc("exec_sql", {"query": sql_drop}).execute()
    print("✅ Step 4: DROP TABLE success.")
    
    print("\n🎉 BRIDGE VERIFIED. FULL AUTONOMY ACHIEVED.")
    
except Exception as e:
    print(f"❌ BRIDGE FAILURE: {e}")
