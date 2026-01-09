import time
import os
import subprocess
import threading
from supabase import create_client, Client
from dotenv import load_dotenv

# Load Env
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Configuration ---
MAX_CONCURRENT_WORKERS = 3  # The Hydra Head Count
POLL_INTERVAL = 5 # Seconds to wait when queue is empty or full

def get_next_lead():
    """Fetches a single lead that is 'ready_to_send'."""
    try:
        # Fetch one lead
        res = supabase.table("leads")\
            .select("*")\
            .eq("status", "ready_to_send")\
            .limit(1)\
            .execute()
            
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def mark_lead_processing(lead_id):
    """Marks lead as 'processing' so other workers don't grab it."""
    supabase.table("leads").update({"status": "processing"}).eq("id", lead_id).execute()

def worker_wrapper(lead):
    """Runs the agent_worker.py script for a lead."""
    print(f"[HYDRA] Spawning Agent for {lead['name']}...")
    
    try:
        # Run the standalone worker script
        cmd = ["python", "agent_worker.py", str(lead['id']), lead['name'], lead['phone']]
        subprocess.run(cmd, check=True)
        print(f"[HYDRA] Agent finished task for {lead['name']}.")
    except Exception as e:
        print(f"[HYDRA] Agent CRASHED for {lead['name']}: {e}")

def main():
    print("=========================================")
    print(f"   HYDRA PROTOCOL INITIATED (Max: {MAX_CONCURRENT_WORKERS})")
    print("=========================================")
    
    active_threads = []
    
    while True:
        # 1. Clean up finished threads
        active_threads = [t for t in active_threads if t.is_alive()]
        
        # 2. Status Report
        print(f"[HYDRA] Active Agents: {len(active_threads)}/{MAX_CONCURRENT_WORKERS}", end="\r")
        
        # 3. Check Capacity
        if len(active_threads) < MAX_CONCURRENT_WORKERS:
            # We have room, look for work
            lead = get_next_lead()
            
            if lead:
                print(f"\n[HYDRA] Target Acquired: {lead['name']}")
                
                # Lock the lead immediately
                mark_lead_processing(lead['id'])
                
                # Launch thread
                t = threading.Thread(target=worker_wrapper, args=(lead,))
                t.start()
                active_threads.append(t)
            else:
                # No leads, nap
                time.sleep(POLL_INTERVAL)
        else:
            # Full capacity, wait for a spot to open
            time.sleep(1)

if __name__ == "__main__":
    main()
