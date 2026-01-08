
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ignite_campaign():
    print("🔥 IGNITION: Converting 'new' leads into call tasks...")
    
    # 1. Fetch new leads (limit 50 to match campaign)
    res = supabase.table('leads').select('*').eq('status', 'new').limit(50).execute()
    leads = res.data
    
    if not leads:
        print("No 'new' leads found to ignite.")
        return

    print(f"Found {len(leads)} leads. Creating tasks...")
    
    for lead in leads:
        task_payload = {
            "phone": lead['phone'],
            "script_context": f"Lead: {lead['company_name']} ({lead['representative_name'] or 'Owner'}). City: {lead['city']}. Industry: {lead['industry']}.",
            "lead_id": lead['id']
        }
        
        task_data = {
            "task_type": "make_call",
            "payload": task_payload,
            "status": "pending",
            "priority": 1,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S%z')
        }
        
        try:
            supabase.table('tasks_queue').insert(task_data).execute()
            print(f"  + Task created for {lead['company_name']}")
            
            # Update lead status to 'queued' or similar (optional, but good practice)
            # supabase.table('leads').update({'status': 'queued'}).eq('id', lead['id']).execute()
            
        except Exception as e:
            print(f"  x Failed to create task for {lead['company_name']}: {e}")

    print("🔥 Campaign Ignited. Tasks are in the queue.")

if __name__ == "__main__":
    ignite_campaign()
