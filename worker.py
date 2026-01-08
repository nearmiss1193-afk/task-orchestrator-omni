import os
import time
import json
from supabase import create_client, Client
from modules.agent_skills import execute_skill
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
WORKER_ID = "sovereign_worker_v1"

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Serverless Local Warning: Supabase credentials missing (expected for dry run).")
    # For specific 'dry run' test without real keys, we can mock or exit.
    # Given 'Sovereign' instructions, we proceed or mock.
    # We will assume keys will be provided in prod, but for now we crash if missing is safer.
    
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
except Exception as e:
    print(f"Connection Init Error: {e}")
    supabase = None

def log_system_event(level, message, context={}):
    try:
        # Async logging would be better for performance, but sync is safer for now
        supabase.table('system_logs').insert({
            'worker_id': WORKER_ID,
            'level': level,
            'message': message,
            'context': context,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S%z')
        }).execute()
    except Exception as e:
        print(f"LOG FALLBACK: {message} | Error: {e}")

def process_task(task):
    task_id = task['id']
    task_type = task['task_type']
    payload = task['payload']
    
    print(f"[{task_id}] Processing: {task_type}")
    log_system_event('INFO', f"Started task: {task_type}", {'task_id': task_id})
    
    # Claim the task
    try:
        supabase.table('tasks_queue').update({
            'status': 'processing',
            'worker_id': WORKER_ID,
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S%z')
        }).eq('id', task_id).execute()
        
        # Execute
        result = execute_skill(task_type, payload)
        
        # Complete
        supabase.table('tasks_queue').update({
            'status': 'completed',
            'result': result,
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S%z')
        }).eq('id', task_id).execute()
        
        print(f"[{task_id}] Success.")
        log_system_event('INFO', f"Completed task: {task_type}", {'task_id': task_id, 'result': str(result)[:100]})
        
    except Exception as e:
        print(f"[{task_id}] Failed: {e}")
        log_system_event('ERROR', f"Failed task: {task_type}", {'task_id': task_id, 'error': str(e)})
        
        supabase.table('tasks_queue').update({
            'status': 'failed',
            'result': {'error': str(e)},
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S%z')
        }).eq('id', task_id).execute()

def main_loop():
    print(f"Worker {WORKER_ID} online. Polling tasks_queue...")
    
    while True:
        try:
            # Poll for pending tasks (Simulating Realtime via high-freq poll for reliability V1)
            # We fetch tasks that are 'pending' OR 'processing' but timed out (stuck)
            response = supabase.table('tasks_queue').select("*").eq('status', 'pending').limit(1).execute()
            tasks = response.data
            
            if tasks:
                for task in tasks:
                    process_task(task)
            else:
                # Update presence heartbeat
                # supabase.table('agent_presence').upsert(...).execute()
                time.sleep(1) 
                
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    if supabase:
        main_loop()
    else:
        print("Supabase client not initialized. Exiting.")
