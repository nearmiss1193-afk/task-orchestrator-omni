import os
import time
import uuid
import random
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Setup Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_mock_task():
    task_types = ['make_call', 'send_email', 'match_lead']
    task_type = random.choice(task_types)
    
    payload = {}
    if task_type == 'make_call':
        payload = {"phone": "+15550102030", "script_context": "Load Test Call"}
    elif task_type == 'send_email':
        payload = {"to": "test@example.com", "subject": "Load Test", "html": "<p>Test</p>"}
    elif task_type == 'match_lead':
        payload = {"lead_id": str(uuid.uuid4())}
        
    return {
        "type": task_type,
        "payload": payload,
        "status": "pending",
        "priority": random.randint(1, 5)
    }

def run_load_test(count=50):
    print(f"🚀 Starting Load Test: Inserting {count} tasks...")
    
    tasks = [generate_mock_task() for _ in range(count)]
    
    # Bulk insert if possible, or loop
    try:
        data = supabase.table("tasks_queue").insert(tasks).execute()
        print(f"✅ Successfully inserted {len(data.data)} tasks.")
    except Exception as e:
        print(f"❌ Batch insert failed: {e}")
        # Retry individually
        for i, task in enumerate(tasks):
            try:
                supabase.table("tasks_queue").insert(task).execute()
                print(f"   Inserted task {i+1}/{count}")
            except Exception as inner_e:
                print(f"   Failed task {i+1}: {inner_e}")
                
    print("\nMonitor the dashboard or 'agent_presence' to see processing speed.")

if __name__ == "__main__":
    run_load_test()
