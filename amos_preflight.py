from supabase import create_client
import os
import json

SUB_URL = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
SUB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo'

def run_preflight():
    supabase = create_client(SUB_URL, SUB_KEY)
    
    # 1. SYSTEM STATE CHECK
    print("--- 1. SYSTEM STATE CHECK ---")
    state_res = supabase.table("system_state") \
        .select("key, status, last_error, build_attempts") \
        .neq("status", "working") \
        .order("status") \
        .execute()
    print(json.dumps(state_res.data, indent=2))

    # 2. HEALTH CHECK
    print("\n--- 2. HEALTH CHECK ---")
    health_res = supabase.table("system_health").select("*").execute()
    print(json.dumps(health_res.data, indent=2))

    # 3. WHAT'S BUILDABLE
    print("\n--- 3. WHAT'S BUILDABLE ---")
    buildable_res = supabase.table("buildable_components").select("*").limit(5).execute()
    print(json.dumps(buildable_res.data, indent=2))

    # 4. LESSONS FOR TOP PRIORITY
    if buildable_res.data:
        top_comp = buildable_res.data[0]["component_name"]
        print(f"\n--- 4. LESSONS FOR {top_comp} ---")
        # Using RPC for lessons if possible, fallback to table query
        try:
            lessons_res = supabase.rpc("get_lessons", {"comp_name": top_comp}).execute()
        except:
            lessons_res = supabase.table("lessons_learned").select("*").eq("component_name", top_comp).execute()
        print(json.dumps(lessons_res.data, indent=2))

if __name__ == "__main__":
    run_preflight()
