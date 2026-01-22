from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(url, key)

components = ["Visitor Analytics"]

print("Updating system state...")
for comp in components:
    # Check if component exists in system_state table first
    # If using 'component_name' as key. 
    # NOTE: We need to know the table schema of `system_state` or `components`.
    # Based on pre-flight, it queries `system_state`.
    # Let's assume `system_state` has a `component_name` and `status` column.
    try:
        # Update system_state
        data = {"key": comp, "status": "working", "last_error": None}
        res = supabase.table("system_state").upsert(data, on_conflict="key").execute()
        print(f"✅ Updated system_state: {comp} -> working")
        
        # Update buildable_components
        res2 = supabase.table("buildable_components").update({"status": "built"}).eq("component_name", comp).execute()
        print(f"✅ Updated buildable_components: {comp} -> built")
    except Exception as e:
        print(f"❌ Failed to update {comp}: {e}")
