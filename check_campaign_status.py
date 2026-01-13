import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_status():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("Error: Missing Supabase credentials")
        return

    client = create_client(url, key)
    
    print("\n📊 CAMPAIGN STATUS REPORT")
    print("=" * 30)
    
    # Leads Funnel
    try:
        total = client.table("leads").select("id", count="exact").execute().count
        contacted = client.table("leads").select("id", count="exact").eq("status", "contacted").execute().count
        new_leads = client.table("leads").select("id", count="exact").eq("status", "new").execute().count
        qualified = client.table("leads").select("id", count="exact").eq("status", "qualified").execute().count
        
        print(f"Total Leads:   {total}")
        print(f"New:           {new_leads}")
        print(f"Contacted:     {contacted} ({(contacted/total*100) if total else 0:.1f}%)")
        print(f"Qualified:     {qualified}")
    except Exception as e:
        print(f"Error fetching leads: {e}")

    # Calls
    print("\n📞 CALL ACTIVITY")
    print("-" * 30)
    try:
        calls = client.table("call_transcripts").select("id", count="exact").execute().count
        print(f"Total Calls:   {calls}")
        
        # Last 3 calls
        recent = client.table("call_transcripts").select("created_at, phone_number, summary").order("created_at", desc=True).limit(3).execute()
        for call in recent.data:
            print(f"- {call.get('created_at', '')[:16]}: {call.get('phone_number')} - {call.get('summary', 'No summary')[:50]}...")
    except Exception as e:
        print(f"Error fetching calls: {e}")

    # Errors
    print("\n⚠️ SYSTEM HEALTH")
    print("-" * 30)
    try:
        errors = client.table("error_logs").select("id", count="exact").execute().count
        recent_err = client.table("error_logs").select("created_at, error_type").order("created_at", desc=True).limit(3).execute()
        
        print(f"Total Errors:  {errors}")
        for err in recent_err.data:
            print(f"- {err.get('created_at', '')[:16]}: {err.get('error_type')}")
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == "__main__":
    get_status()
